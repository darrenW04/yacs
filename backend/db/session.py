from datetime import datetime
from db.model import * # Assuming this is your base model with self.db
import uuid

class Session(Model):
    # The __init__ is not needed if it only calls super()

    @staticmethod
    def _create_session_id() -> str:
        """
        Generates a secure, random UUID (version 4).
        Made static as it doesn't use 'self'.
        """
        return str(uuid.uuid4())

    def start_session(self, user_id: int):
        """
        Starts a new session for a user.
        Generates its own session_id and start_time.
        """
        session_id = self._create_session_id()
        start_time = datetime.utcnow()
        
        sql = """INSERT INTO public.user_session (session_id, user_id, start_time) 
                 VALUES (%s, %s, %s)
                 RETURNING session_id;""" # Return the new ID
        args = (session_id, user_id, start_time)
        
        # Assumes db.execute returns a list of results
        result = self.db.execute(sql, args, is_select=True)
        return result[0]['session_id'] if result else None

    def get_session(self, session_id: str):
        """
        Gets a specific session using an exact '=' match.
        The session_id is now a required argument.
        """
        sql = """SELECT session_id, user_id, start_time, end_time 
                 FROM public.user_session
                 WHERE session_id = %s;"""
        args = (session_id,)
        
        result = self.db.execute(sql, args, is_select=True)
        return result[0] if result else None

    def end_session(self, session_id: str):
        """
        Ends a specific session using an exact '=' match.
        The session_id is required, preventing mass updates.
        """
        # Fixes the mutable default by getting the time *inside* the function.
        end_time = datetime.utcnow()

        sql = """UPDATE public.user_session 
                 SET end_time = %s 
                 WHERE session_id = %s;"""
        args = (end_time, session_id)
        
        # Assuming db.execute returns a status or row count for non-select queries
        return self.db.execute(sql, args, is_select=False)