import sqlite3


class DBHelper:

  def __init__(self, dbname="todo.sqlite"):
    self.dbname = dbname
    self.conn = sqlite3.connect(dbname)

  def setup(self):
    stmt = "CREATE TABLE IF NOT EXISTS calendars (calname text, password text, emoji text)"
    self.conn.execute(stmt)
    stmt = "CREATE TABLE IF NOT EXISTS access (userid int, calname text)"
    self.conn.execute(stmt)
    stmt = "CREATE TABLE IF NOT EXISTS events (calname text, eventname text, date timestamp, notes text)"
    self.conn.execute(stmt)
    stmt = "CREATE TABLE IF NOT EXISTS presets (userid int, preset int, calname text, see_notes text)"
    self.conn.execute(stmt)
    self.conn.commit()

  def add_calendar(self, calname, password, emoji, userid):
    stmt = "INSERT INTO calendars (calname, password, emoji) VALUES (?, ?, ?)"
    args = (
        calname,
        password,
        emoji,
    )
    self.conn.execute(stmt, args)

    stmt = "INSERT INTO access (userid, calname) VALUES (?, ?)"
    args = (
        userid,
        calname,
    )
    self.conn.execute(stmt, args)
    self.conn.commit()

  def add_event(self, calname, eventname, date, notes):
    stmt = "INSERT INTO events (calname, eventname, date, notes) VALUES (?, ?, ?, ?)"
    args = (
        calname,
        eventname,
        date,
        notes,
    )
    self.conn.execute(stmt, args)
    self.conn.commit()

  def add_to_preset(self, userid, preset, calname):
    stmt = "INSERT INTO presets (userid, preset, calname) VALUES (?, ?, ?)"
    args = (
        userid,
        preset,
        calname,
    )
    self.conn.execute(stmt, args)
    self.conn.commit()

  def set_notes_for_preset(self, userid, preset, notes):
    stmt = "UPDATE presets SET see_notes = (?) WHERE userid = (?) AND preset = (?)"
    args = (
        notes,
        userid,
        preset,
    )
    self.conn.execute(stmt, args)
    self.conn.commit()

  def grant_access(self, userid, calname):
    stmt = "INSERT INTO access (userid, calname) VALUES (?, ?)"
    args = (
        userid,
        calname,
    )
    self.conn.execute(stmt, args)
    self.conn.commit()

  def remove_access(self, calname, userid):
    stmt = "DELETE FROM access WHERE calname = (?) AND userid = (?)"
    args = (
        calname,
        userid,
    )
    self.conn.execute(stmt, args)
    self.conn.commit()

  def delete_event(self, calname, eventname, date):
    stmt = "DELETE FROM events WHERE calname = (?) AND eventname = (?) AND date = (?)"
    args = (
        calname,
        eventname,
        date,
    )
    self.conn.execute(stmt, args)
    self.conn.commit()

  def get_all_calendars(self):
    stmt = "SELECT calname FROM calendars"
    return [x[0] for x in self.conn.execute(stmt)]

  def get_my_calendars(self, userid):
    stmt = "SELECT calname FROM access WHERE userid = (?)"
    args = (userid, )
    return [x[0] for x in self.conn.execute(stmt, args)]

  def get_emoji(self, calname):
    stmt = "SELECT emoji FROM calendars WHERE calname = (?)"
    args = (calname, )
    return [x[0] for x in self.conn.execute(stmt, args)][0]

  def get_all_calendars_emoji(self):
    stmt = "SELECT calname, emoji FROM calendars"
    return [x[0:2] for x in self.conn.execute(stmt)]

  def get_my_calendars_emoji(self, userid):
    stmt = "SELECT calendars.calname, calendars.emoji FROM access JOIN calendars ON access.calname = calendars.calname WHERE access.userid = (?)"
    args = (userid, )
    return [x[0:2] for x in self.conn.execute(stmt, args)]

  def get_events(self, calname):
    stmt = "SELECT date, calname, eventname, notes FROM events WHERE calname = (?) ORDER BY date"
    args = (calname, )
    return [x[0:4] for x in self.conn.execute(stmt, args)]

  def has_events(self, cals):
    question_marks = ', '.join('?' for _ in cals)
    stmt = f"SELECT EXISTS (SELECT 1 FROM events WHERE calname IN ({question_marks}));"
    args = tuple(cals, )
    result = self.conn.execute(stmt, args).fetchone()
    return bool(result[0])

  def get_access(self, calname):
    stmt = "SELECT userid FROM access WHERE calname = (?)"
    args = (calname, )
    return [x[0] for x in self.conn.execute(stmt, args)]

  def get_password(self, calname):
    stmt = "SELECT password FROM calendars WHERE calname = (?)"
    args = (calname, )
    return [x[0] for x in self.conn.execute(stmt, args)][0]

  def get_preset(self, userid, preset):
    stmt = "SELECT calname, see_notes FROM presets WHERE userid = (?) AND preset = (?)"
    args = (
        userid,
        preset,
    )
    return [x[0:2] for x in self.conn.execute(stmt, args)]

  def clear_preset(self, userid, preset):
    stmt = "DELETE FROM presets WHERE userid = (?) AND preset = (?)"
    args = (
        userid,
        preset,
    )
    self.conn.execute(stmt, args)
    self.conn.commit()

  def drop_table(self):
    stmt = "DROP TABLE IF EXISTS calendars;"
    self.conn.execute(stmt)
    stmt = "DROP TABLE IF EXISTS access;"
    self.conn.execute(stmt)
    stmt = "DROP TABLE IF EXISTS events;"
    self.conn.execute(stmt)
    stmt = "DROP TABLE IF EXISTS presets;"
    self.conn.execute(stmt)
    self.conn.commit()
