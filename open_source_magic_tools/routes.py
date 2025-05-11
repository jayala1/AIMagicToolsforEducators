from flask import Blueprint, render_template, request, redirect, url_for, session, current_app
# Use relative imports within the package
from .ollama_utils import generate_text, list_ollama_models
from .config import DEFAULT_OLLAMA_MODEL, DEFAULT_OPENAI_MODEL, OPENAI_API_KEY, OLLAMA_URL

# Create a Blueprint
bp = Blueprint('main', __name__)

@bp.route('/', methods=['GET', 'POST'])
def index():
    ollama_models = []
    ollama_connection_error = session.pop('ollama_connection_error', None) # Get and remove error from session

    if request.method == 'POST':
        session['inference_server'] = request.form.get('inference_server')
        session['ollama_ip'] = request.form.get('ollama_ip', 'http://localhost:11434') # Store Ollama IP
        session['ollama_model'] = request.form.get('ollama_model', DEFAULT_OLLAMA_MODEL)
        session['openai_model'] = request.form.get('openai_model', DEFAULT_OPENAI_MODEL)

        # Update the OLLAMA_URL in config based on user input
        current_app.config['OLLAMA_URL'] = session['ollama_ip']

        # If Ollama is selected, try to fetch models AFTER saving settings
        if session['inference_server'] == 'ollama':
            ollama_models = list_ollama_models()
            if not ollama_models:
                session['ollama_connection_error'] = "Failed to connect to Ollama or list models. Please check the IP and if Ollama is running."
            else:
                 # If models are fetched successfully, store them and the selected model in the session
                 session['ollama_available_models'] = ollama_models
                 # Ensure the selected model is one of the available models, or default
                 if session['ollama_model'] not in ollama_models:
                     session['ollama_model'] = DEFAULT_OLLAMA_MODEL if DEFAULT_OLLAMA_MODEL in ollama_models else (ollama_models[0] if ollama_models else '')


        return redirect(url_for('main.index')) # Redirect to GET after POST

    # --- GET Request Handling ---

    # Get current settings from session
    inference_server = session.get('inference_server', 'ollama')
    ollama_ip = session.get('ollama_ip', 'http://localhost:11434')
    ollama_model = session.get('ollama_model', DEFAULT_OLLAMA_MODEL)
    openai_model = session.get('openai_model', DEFAULT_OPENAI_MODEL)

    # Update the OLLAMA_URL in config based on session data on GET request
    current_app.config['OLLAMA_URL'] = ollama_ip

    # Get the list of available models from the session (populated on POST)
    ollama_models = session.get('ollama_available_models', [])

    # If Ollama is selected and no models are in session, try a fetch (fallback for initial load)
    # This is a less reliable fetch than the POST, but provides a chance on first load
    if inference_server == 'ollama' and not ollama_models:
         ollama_models = list_ollama_models()
         if not ollama_models:
              ollama_connection_error = "Failed to connect to Ollama or list models on initial load. Please check the IP and click 'Save Settings and Fetch Models'."
         else:
              session['ollama_available_models'] = ollama_models
              # Ensure the selected model is one of the available models, or default
              if ollama_model not in ollama_models:
                  ollama_model = DEFAULT_OLLAMA_MODEL if DEFAULT_OLLAMA_MODEL in ollama_models else (ollama_models[0] if ollama_models else '')
                  session['ollama_model'] = ollama_model


    return render_template(
        'index.html',
        inference_server=inference_server,
        ollama_ip=ollama_ip,
        ollama_model=ollama_model,
        openai_model=openai_model,
        ollama_models=ollama_models,
        ollama_connection_error=ollama_connection_error,
        OPENAI_API_KEY=OPENAI_API_KEY
    )

@bp.route('/social_media_post', methods=['GET', 'POST'])
def social_media_post():
    generated_post = None
    inference_server = session.get('inference_server', 'ollama')
    model_name = None

    if inference_server == 'ollama':
        model_name = session.get('ollama_model', DEFAULT_OLLAMA_MODEL)
    elif inference_server == 'openai':
        model_name = session.get('openai_model', DEFAULT_OPENAI_MODEL)

    if request.method == 'POST':
        topic = request.form.get('topic')
        audience = request.form.get('audience')
        tone = request.form.get('tone')

        if not topic:
            generated_post = "Please provide a topic."
        else:
            # The generate_text function now uses the OLLAMA_URL from config
            generated_post = generate_text(prompt=f"Generate a strong social media post about {topic}. The target audience is {audience if audience else 'general'} and the tone should be {tone if tone else 'neutral'}.**Provide only the text of the post, without any introductory or concluding remarks.**",
                                           model_type=inference_server,
                                           model_name=model_name)

    return render_template(
        'tool_social_media_post.html',
        generated_post=generated_post,
        inference_server=inference_server,
        model_name=model_name,
        # Pass back form values to retain input after POST
        topic=request.form.get('topic', ''),
        audience=request.form.get('audience', ''),
        tone=request.form.get('tone', '')
    )

@bp.route('/lesson_hook', methods=['GET', 'POST'])
def lesson_hook():
    generated_hook = None
    inference_server = session.get('inference_server', 'ollama')
    model_name = None

    if inference_server == 'ollama':
        model_name = session.get('ollama_model', DEFAULT_OLLAMA_MODEL)
    elif inference_server == 'openai':
        model_name = session.get('openai_model', DEFAULT_OPENAI_MODEL)

    if request.method == 'POST':
        subject_topic = request.form.get('subject_topic')
        grade_level = request.form.get('grade_level')
        tone = request.form.get('tone')
        hook_type = request.form.get('hook_type')
        time_limit = request.form.get('time_limit')
        special_instructions = request.form.get('special_instructions')

        if not subject_topic or not grade_level:
            generated_hook = "Please provide the Subject/Topic and Grade Level."
        else:
            prompt = f"Generate a lesson hook for a lesson about {subject_topic} for students in grade {grade_level}. "

            if tone:
                prompt += f"The tone should be {tone}. "
            if hook_type:
                prompt += f"The type of hook should be a {hook_type}. "
            if time_limit:
                prompt += f"The hook should be suitable for a {time_limit} introduction. "
            if special_instructions:
                prompt += f"Additional instructions: {special_instructions}. "

            prompt += "Ensure the hook captures attention, sparks curiosity, connects prior knowledge, and sets the stage for learning."

            generated_hook = generate_text(prompt, inference_server, model_name)

    return render_template(
        'tool_lesson_hook.html',
        generated_hook=generated_hook,
        inference_server=inference_server,
        model_name=model_name,
        # Pass back form values to retain input after POST
        subject_topic=request.form.get('subject_topic', ''),
        grade_level=request.form.get('grade_level', ''),
        tone=request.form.get('tone', ''),
        hook_type=request.form.get('hook_type', ''),
        time_limit=request.form.get('time_limit', ''),
        special_instructions=request.form.get('special_instructions', '')
    )


@bp.route('/math_spiral_review', methods=['GET', 'POST'])
def math_spiral_review():
    generated_review = None
    inference_server = session.get('inference_server', 'ollama')
    model_name = None

    if inference_server == 'ollama':
        model_name = session.get('ollama_model', DEFAULT_OLLAMA_MODEL)
    elif inference_server == 'openai':
        model_name = session.get('openai_model', DEFAULT_OPENAI_MODEL)

    # Define lists for dropdowns and checkboxes for the template
    grade_level_options = ['Pre-K', 'K', '1st Grade', '2nd Grade', '3rd Grade', '4th Grade', '5th Grade', '6th Grade', '7th Grade', '8th Grade']
    common_topics = ['Addition', 'Subtraction', 'Multiplication', 'Division', 'Fractions', 'Decimals', 'Percentages', 'Geometry', 'Measurement', 'Word Problems', 'Algebra Basics', 'Data Analysis']
    difficulty_options = ['Easy', 'Medium', 'Hard', 'Challenge']
    question_type_options = ['Multiple Choice', 'Open-Ended', 'Word Problems']

    if request.method == 'POST':
        grade_level = request.form.get('grade_level')
        topics_covered = request.form.getlist('topics_covered') # Use getlist for checkboxes
        todays_focus = request.form.get('todays_focus')
        difficulty = request.form.get('difficulty')
        num_questions = request.form.get('num_questions')
        question_types = request.form.getlist('question_types') # Use getlist for checkboxes
        special_instructions = request.form.get('special_instructions')


        if not grade_level or not topics_covered or not num_questions or not question_types:
            generated_review = "Please provide Grade Level, Topics Covered, Number of Questions, and Question Types."
        else:
            prompt = f"Create a {num_questions}-question spiral math review for {grade_level} students. "

            prompt += f"Topics to pull from: {', '.join(topics_covered)}. "

            if todays_focus:
                prompt += f"Today's lesson focus is {todays_focus}, so include 1-2 questions on this topic. "

            if difficulty:
                prompt += f"The questions should be {difficulty} difficulty. "

            prompt += f"Use a mix of question types: {', '.join(question_types)}. "

            if special_instructions:
                prompt += f"Additional instructions: {special_instructions}. "

            prompt += "Ensure the questions are varied and appropriate for the grade level standards. Format the output clearly, numbering each question and indicating the topic and type if possible."


            generated_review = generate_text(prompt, inference_server, model_name)


    return render_template(
        'tool_math_spiral_review.html',
        generated_review=generated_review,
        inference_server=inference_server,
        model_name=model_name,
        # Pass back form values to retain input after POST
        grade_level=request.form.get('grade_level', ''),
        topics_covered=request.form.getlist('topics_covered'), # Retain selected checkboxes
        todays_focus=request.form.get('todays_focus', ''),
        difficulty=request.form.get('difficulty', ''),
        num_questions=request.form.get('num_questions', ''),
        question_types=request.form.getlist('question_types'), # Retain selected checkboxes
        special_instructions=request.form.get('special_instructions', ''),
        # Pass options to the template
        grade_level_options=grade_level_options,
        common_topics=common_topics,
        difficulty_options=difficulty_options,
        question_type_options=question_type_options
    )

@bp.route('/decodable_text', methods=['GET', 'POST'])
def decodable_text():
    generated_text = None
    inference_server = session.get('inference_server', 'ollama')
    model_name = None

    if inference_server == 'ollama':
        model_name = session.get('ollama_model', DEFAULT_OLLAMA_MODEL)
    elif inference_server == 'openai':
        model_name = session.get('openai_model', DEFAULT_OPENAI_MODEL)

    # Define the list of phonics patterns for the template
    phonics_patterns = [
        "m /m/ am", "t /t/ at, mat", "s /s/ sat", "p /p/ sat, tap", "i /ĭ/ sit, tip",
        "f /f/ fit, if", "n /n/ nip, tin", "o /ŏ/ on, pot", "d /d/ mad, dim", "r /r/ rat, rid",
        "u /ŭ/ pup, sum", "c /k/ cod, cub", "g /g/ gut, dig", "b /b/ ban, bib", "e /ĕ/ set, bed",
        "h /h/ hem, hip", "l /l/ lid, lag", "k /k/ kid, kin", "j /j/ jug, jam", "w /w/ wax, wit",
        "v /v/ vet, van", "z /z/ zip, zig", "y /y/ yes, yet", "qu /kw/ quit, quiz", "x /ks/ box, six",
        "sh /sh/ ship, shop", "ch /ch/ chin, chip", "th /th/ that, them", "th /th/ thin, path",
        "wh /wh/ when, whip", "ng /ŋ/ ring, sing", "ck /k/ back, duck", "ll /l/ fill, well",
        "ss /s/ pass, mess", "zz /z/ buzz, jazz", "ff /f/ puff, cliff", "ay /ā/ day, play",
        "ee /ē/ see, tree", "igh /ī/ high, sigh", "ow /ō/ snow, grow", "ew /ū/ few, new",
        "oa /ō/ boat, road", "ai /ā/ rain, sail", "ie /ī/ pie, tie", "ou /ou/ out, shout",
        "oy /oi/ boy, toy", "oi /oi/ boil, coin", "ar /är/ car, star", "or /ôr/ for, horn",
        "er /ər/ her, fern", "ir /ər/ bird, girl", "ur /ər/ fur, turn", "ear /ēr/ dear, fear",
        "air /air/ hair, pair", "ure /yoor/ pure, cure", "tch /ch/ catch, match", "dge /j/ bridge, edge",
        "kn /n/ know, knit", "wr /r/ write, wrong", "le /əl/ table, apple", "mb /m/ comb, lamb",
        "gn /n/ sign, gnaw", "ph /f/ phone, graph", "oe /ō/ toe, hoe", "au /aw/ haul, sauce",
        "aw /aw/ jaw, claw", "al /aw/ walk, talk", "eigh /ā/ eight, sleigh", "ei /ā/ vein, weight",
        "ey /ē/ key, monkey", "y /ē/ happy, bunny", "y /ī/ cry, fly", "ce /s/ face, ice",
        "ge /j/ cage, stage", "ci /sh/ special, social", "ti /sh/ station, motion", "si /sh/ mansion, tension",
        "si /zh/ vision, decision", "sc /s/ scene, scent", "gue /g/ league, rogue", "que /k/ antique, plaque",
        "-ed /t/ looked, jumped", "-ed /d/ played, called", "-ed /id/ wanted, painted", "-ing /ing/ running, jumping",
        "-er /ər/ runner, jumper", "-est /əst/ biggest, fastest", "un- /ʌn/ unlock, unhappy", "re- /rē/ redo, rewrite",
        "pre- /prē/ preview, prepare", "mis- /mɪs/ misbehave, misplace", "dis- /dɪs/ disconnect, dislike",
        "-less /ləs/ helpless, fearless", "-ful /fəl/ helpful, thankful", "-ness /nəs/ darkness, kindness",
        "-ment /mənt/ payment, movement", "-ly /lē/ slowly, kindly", "-able /əbl/ readable, lovable",
        "-ible /ɪbl/ visible, possible", "-tion /shən/ action, station", "-sion /zhən/ vision, decision"
    ]

    if request.method == 'POST':
        selected_patterns = request.form.getlist('phonics_patterns') # Use getlist for checkboxes
        num_texts = request.form.get('num_texts', 1) # Default to 1 text
        special_instructions = request.form.get('special_instructions')

        if not selected_patterns:
            generated_text = "Please select at least one phonics pattern."
        else:
            prompt = f"Generate {num_texts} short, decodable texts for early readers. "
            prompt += f"These texts should primarily use words that contain the following phonics patterns: {', '.join(selected_patterns)}. "
            prompt += "Keep sentences simple and repetitive. "

            if special_instructions:
                prompt += f"Additional instructions: {special_instructions}. "

            prompt += "Format each text clearly, perhaps labeling them Text 1, Text 2, etc."

            generated_text = generate_text(prompt, inference_server, model_name)

    return render_template(
        'tool_decodable_text.html',
        generated_text=generated_text,
        inference_server=inference_server,
        model_name=model_name,
        # Pass back form values to retain input after POST
        selected_patterns=request.form.getlist('phonics_patterns'), # Retain selected checkboxes
        num_texts=request.form.get('num_texts', 1),
        special_instructions=request.form.get('special_instructions', ''),
        # Pass the phonics patterns list to the template
        phonics_patterns=phonics_patterns
    )

@bp.route('/lesson_plan', methods=['GET', 'POST'])
def lesson_plan():
    generated_lesson_plan = None
    inference_server = session.get('inference_server', 'ollama')
    model_name = None

    if inference_server == 'ollama':
        model_name = session.get('ollama_model', DEFAULT_OLLAMA_MODEL)
    elif inference_server == 'openai':
        model_name = session.get('openai_model', DEFAULT_OPENAI_MODEL)

    # Define the list of grade levels for the template
    grade_level_options = [
        'Pre-K', 'Kindergarten', '1st Grade', '2nd Grade', '3rd Grade',
        '4th Grade', '5th Grade', '6th Grade', '7th Grade', '8th Grade',
        '9th Grade', '10th Grade', '11th Grade', '12th Grade', 'University'
    ]

    if request.method == 'POST':
        grade_level = request.form.get('grade_level')
        topic_standard_objective = request.form.get('topic_standard_objective')
        additional_criteria = request.form.get('additional_criteria')
        standards_to_align = request.form.get('standards_to_align')

        if not grade_level or not topic_standard_objective:
            generated_lesson_plan = "Please provide the Grade Level and Topic, Standard, or Objective."
        else:
            prompt = f"Generate a lesson plan for students in {grade_level}. "
            prompt += f"The lesson is based on the following topic, standard, or objective: {topic_standard_objective}. "

            if additional_criteria:
                prompt += f"Include the following additional criteria: {additional_criteria}. "
            if standards_to_align:
                prompt += f"Align the lesson plan to the following standards: {standards_to_align}. "

            prompt += "Provide a comprehensive lesson plan structure including objectives, materials, procedures, assessment, and differentiation."


            generated_lesson_plan = generate_text(prompt, inference_server, model_name)

    return render_template(
        'tool_lesson_plan.html',
        generated_lesson_plan=generated_lesson_plan,
        inference_server=inference_server,
        model_name=model_name,
        # Pass back form values to retain input after POST
        grade_level=request.form.get('grade_level', ''),
        topic_standard_objective=request.form.get('topic_standard_objective', ''),
        additional_criteria=request.form.get('additional_criteria', ''),
        standards_to_align=request.form.get('standards_to_align', ''),
        # Pass the grade level options to the template
        grade_level_options=grade_level_options
    )

# Add routes for other tools here as you implement them