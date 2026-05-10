from http.client import responses

from src.database.config import supabase, get_supabase
import bcrypt

def _client():
    """Return an active Supabase client or raise a clear error if not configured."""
    client = supabase or get_supabase()
    if client is None:
        raise RuntimeError(
            "Supabase client is not configured. Set SUPABASE_URL and SUPABASE_KEY in Streamlit secrets."
        )
    return client


def check_teacher_exists(username: str):
    # Check if a teacher with the given username already exists in the database, if exist return True else False
    response = _client().table("teachers").select("username").eq("username", username).execute()
    return len(response.data) > 0

def create_teacher(username: str, password: str, name: str):
    # Create a new teacher in the database with the given username and password, return True if created successfully else False
    if check_teacher_exists(username):
        return False

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    data = {"username": username, "password": hashed_password, "name": name}


    response = _client().table("teachers").insert(data).execute()
    return response.data

def teacher_login(username: str, password: str):
    # Check if the given username and password match with any teacher in the database, return True if match else False
    response = _client().table("teachers").select("*").eq("username", username).execute()
    if len(response.data) == 0:
        return False

    teacher = response.data[0]
    if bcrypt.checkpw(password.encode('utf-8'), teacher['password'].encode('utf-8')):
        return teacher
    return None

def get_all_students():
    reponse = _client().table("students").select("*").execute()
    return reponse.data

def create_student(name_name, face_embedding=None, voice_embedding=None):
    data = {"name": name_name, "face_embedding": face_embedding, "voice_embedding": voice_embedding}
    response = _client().table("students").insert(data).execute()
    return response.data

def create_subject(sub_code, sub_name, sub_section, teacher_id):
    data = {"subject_code": sub_code, "name": sub_name, "section": sub_section, "teacher_id": teacher_id}
    response = _client().table("subjects").insert(data).execute()
    return response.data

def get_teacher_subjects(teacher_id):
    response = _client().table('subjects').select('*, subject_students(count), attendance_logs(timestamp)').eq('teacher_id', teacher_id).execute()
    subjects =  response.data

    for sub in subjects:
        sub['total_students'] = sub.get('subject_students', [{}])[0].get('count', 0) if sub.get('subject_students') else 0
        attendance = sub.get('attendance_logs', [])
        unique_sessions = len(set(log['timestamp'] for log in attendance))
        sub['total_classes'] = unique_sessions

        sub.pop('Subject_students', None)
        sub.pop('attendance_logs', None)
    return subjects