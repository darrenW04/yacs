from fastapi import HTTPException
from db.session import Session as SessionModel
from db.user import User as UserModel
from common import verify_password  # <-- Import the SECURE verification function
from api_models import SessionCreate, SessionDelete # <-- Import Pydantic models

# --- Instantiate models ONCE at the module level ---
sessions = SessionModel()
users = UserModel()

def add_session(credentials: SessionCreate):
    """
    Logs a user in by verifying their email and password.
    Creates a new session if successful.
    """
    # 1. Get user by email ONLY
    user_list = users.get_user(email=credentials.email, enable=True)
    
    # Use a generic error for security (don't tell attacker if email or pass was wrong)
    if not user_list:
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    user_data = user_list[0]
    stored_hash = user_data['password']

    # 2. Securely verify the password against the hash
    if not verify_password(credentials.password, stored_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    # 3. If password is correct, create a session
    # We use the optimized start_session that only needs a user_id
    uid = user_data['user_id']
    session = sessions.start_session(uid) # Assumes start_session returns the new session dict

    if not session:
        raise HTTPException(status_code=500, detail="Failed to start a new session.")

    # 4. Return the success data
    return {
        "sessionID": session['session_id'], 
        "uid": uid, 
        "startTime": str(session['start_time']),
        "userName" : user_data['name']
    }

def delete_session(session_data: SessionDelete):
    """
    Logs a user out by ending their session.
    """
    given_session_id = session_data.sessionID

    # 1. Check if the session exists
    session_found = sessions.get_session(session_id=given_session_id)
    if not session_found:
        raise HTTPException(status_code=404, detail="Session not found.")

    # 2. Check if it's already logged out
    if session_found['end_time'] is not None:
        raise HTTPException(status_code=400, detail="This session is already expired.")

    # 3. End the session (using the optimized method)
    res = sessions.end_session(session_id=given_session_id)
    if res is None:
        raise HTTPException(status_code=500, detail="Failed to end this session.")

    return {"status": "success", "sessionID": given_session_id}