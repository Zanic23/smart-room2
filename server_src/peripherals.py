import json

import database

class Peripheral:
    def handle_post(self, req):
        raise NotImplementedError()

    def handle_get(self, req):
        raise NotImplementedError()

    def get_username(self, req):
        return req["values"]["user"]

def get_req_args(req, *names):
    retval = []
    for name in names:
        if name in req["args"]:
            retval.append(req["values"][name])
        else:
            retval.append(None)
    return tuple(retval)

class Locks(Peripheral):
    @database.sql_connection
    def handle_post(self, cursor, req):
        lock_state = self.get_lock_state(cursor, req)
        was_opened, should_unlock = get_req_args(req, "was_opened", "should_unlock")
        if was_opened is not None:
            lock_state.open_door()
        if should_unlock is not None:
            lock_state.should_unlock = bool(should_unlock == "True")
        database.save_user(cursor, self.get_username(req), lock_state=lock_state)
        return "Successfully Updated Lock State"

    @database.sql_connection
    def handle_get(self, cursor, req):
        lock_state = self.get_lock_state(cursor, req)
        retval = lock_state.to_json()
        #we need to update should_unlock to false for next request
        if lock_state.should_unlock:
            lock_state.should_unlock = False
        database.save_user(cursor, self.get_username(req), lock_state=lock_state)
        return retval

    def get_lock_state(self, cursor, req):
        return database.get_user(cursor, self.get_username(req))[database.LockState.index]

class Colors(Peripheral):
    @database.sql_connection
    def handle_post(self, cursor, req):
        color_state = self.get_color_state(cursor, req)
        rgb_list, room_lights = get_req_args(req, "rgb", "room_lights")
        if rgb_list is not None:
            color_state.rgb = json.loads(f"[{rgb_list}]")
        if room_lights is not None:
            color_state.room_lights = bool(room_lights == "True")
        database.save_user(cursor, self.get_username(req), color_state=color_state)
        return f"Successfully Update Color State"

    @database.sql_connection
    def handle_get(self, cursor, req):
        return self.get_color_state(cursor, req).to_json()

    def get_color_state(self, cursor, req):
        return database.get_user(cursor, self.get_username(req))[database.ColorState.index]

class Camera(Peripheral):
    def handle_post(self, req):
        pass

    def handle_get(self, req):
        pass