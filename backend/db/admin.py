class Admin:

	def __init__(self, db_conn):
		self.db_conn = db_conn
		self.interface_name = 'admin_info'

	def get_semester_default(self):
		# Use COALESCE of scalar subselects to return a single deterministic value.
		# This avoids UNION/LIMIT and is clearer about precedence: admin_settings takes priority.
		query = """
		SELECT COALESCE(
		  (SELECT admin.semester FROM admin_settings admin LIMIT 1),
		  (SELECT si.semester FROM semester_info si WHERE si.public = true LIMIT 1)
		) AS semester
		"""
		result, error = self.db_conn.execute(query, None, True)

		if error:
			return (None, error)

		if not result:
			return (None, None)

		# result is a list-like with one row containing 'semester'
		return (result[0].get('semester'), None)

