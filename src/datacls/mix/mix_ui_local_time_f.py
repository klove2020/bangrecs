from src.sql.connect import connect_sql

class MixUiLocalTime:
    def update_active_user_local_time(self):
        uid_list = self.active_user_list
        return self.update_user_local_time(uid_list)

    def update_user_local_time(self, uid_list):
        num = 0
        for uid in uid_list:
            num += 1
            self.matain_single_user_loacl_time(uid)
            
            if num % 100 == 0:
                print(f"matained {uid=}")


    def matain_single_user_loacl_time(self, uid):
        u = self.get_user(uid)  # Assuming this function returns a user object with a local_update_time dictionary
        connection, cursor = connect_sql()

        for t in [1, 2, 3, 4, 6]:
            try:
                query = "SELECT MAX(timestamp) as max_timestamp FROM collect WHERE uid=%s AND subject_type=%s"
                cursor.execute(query, (int(uid), t))
                result = cursor.fetchone()
                max_timestamp = result[0]

                if max_timestamp is not None:
                    u.local_update_time[t] = max_timestamp
            except Exception as e:
                print(f"Error fetching max timestamp for subject_type {t}: {e}")

        cursor.close()

