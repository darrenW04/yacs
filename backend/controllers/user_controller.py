from fastapi import HTTPException
from db.user import User as UserModel
from db.session import Session as SessionModel
from common import hash_password, verify_password  # <-- Import the new secure functions
from api_models import updateUser, UserDeletePydantic, UserCreatePydantic 

# --- Instantiate models ONCE at the module level ---
users = UserModel()
sessions = SessionModel()

def get_user_info(session_id: str):
    """
    Gets user information from a valid session ID.
    """
    session_data = sessions.get_session(session_id)
    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found.")

    if session_data['end_time'] is not None:
        raise HTTPException(status_code=401, detail="This session has expired.")

    uid = session_data['user_id']
    user_list = users.get_user(uid=uid) 

    if not user_list:
        raise HTTPException(status_code=404, detail="User not found for this session.")

    user_data = user_list[0] 

    return {
        "uid": user_data['uid'],
        "name": user_data['name'],
        "email": user_data['email'],
        "phone": user_data['phone'],
        "major": user_data['major'],
        "degree": user_data['degree']
    }

def update_user(user_update: updateUser):
    """
    Updates a user's profile.
    Pydantic has already validated that required fields exist.
    """
    if len(user_update.newPassword) > 255:
        raise HTTPException(status_code=400, detail="Password cannot exceed 255 characters.")

    session_data = sessions.get_session(user_update.sessionID)
    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found.")
    
    if session_data['end_time'] is not None:
        raise HTTPException(status_code=401, detail="This session has expired.")

    uid = session_data['user_id']

    args = {
        "Name": user_update.name,
        "Email": user_update.email,
        "Phone": user_update.phone,
        "Password": hash_password(user_update.newPassword), # <-- Use hash_password
        "Major": user_update.major,
        "Degree": user_update.degree,
        "UID": uid
    }
    ret = users.update_user(args)

    if ret is None: 
        raise HTTPException(status_code=500, detail="Failed to update user profile.")

    return {"status": "success", "message": "User profile updated."}

def delete_user(credentials: UserDeletePydantic):
    """
    Deletes a user after verifying their password.
    """
    session_data = sessions.get_session(credentials.sessionID)
    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found.")

    if session_data['end_time'] is not None:
        raise HTTPException(status_code=401, detail="This session has expired.")

    uid = session_data['user_id']

    # --- Secure Password Verification ---
    # 1. Get the user by ID first
    user_list = users.get_user(uid=uid, enable=True)
    if not user_list:
        raise HTTPException(status_code=404, detail="User not found.")

    # 2. Get their stored password hash from the database
    stored_hash = user_list[0]['password'] 

    # 3. Verify the plain-text password against the hash
    if not verify_password(credentials.password, stored_hash):
        raise HTTPException(status_code=401, detail="Wrong password.")
    # --- End Verification ---

    # If verification passed, delete the user
    ret = users.delete_user(uid)
    if ret is None:
        raise HTTPException(status_code=500, detail="Failed to delete user.")

    # Revoke *this specific session*
    sessions.end_session(credentials.sessionID)

    return {"status": "success", "uid": uid, "message": "User deleted."}

def add_user(new_user: UserCreatePydantic):
    """
    Creates a new user.
    Pydantic handles most validation.
    """
    findUser = users.get_user(email=new_user.email, enable=True)
    if findUser:
        raise HTTPException(status_code=409, detail="User already exists (Email already in use).")

    args = {
        "Name": new_user.name,
        "Email": new_user.email,
        "Phone": new_user.phone,
        "Password": hash_password(new_user.password), # <-- Use hash_password
        "Major": new_user.major,
        "Degree": new_user.degree,
        "Enable": True
    }
    res = users.add_user(args)
    if res is None:
        raise HTTPException(status_code=500, detail="Failed to add user.")

    return {"status": "success", "message": "User added successfully."}