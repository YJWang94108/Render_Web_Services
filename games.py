import secrets
import string

def generate_room_code():

    characters = string.ascii_uppercase + string.digits

    return "".join(
        secrets.choice(characters)
        for _ in range(6)
    )

def get_game_players(supabase, room_code):

    response = (
        supabase
        .table("games")
        .select("id")
        .eq("room_code", room_code)
        .execute()
    )

    if not response.data:
        return []

    game_id = response.data[0]["id"]

    response = (
        supabase
        .table("game_players")
        .select(
            "user_id, users(username)"
        )
        .eq("game_id", game_id)
        .execute()
    )

    return response.data

def broadcast_players(socketio, supabase, room_code, socket_users):

    players = get_game_players(supabase,room_code)

    online_users = get_online_users(socket_users, room_code)

    socketio.emit(
        "players_updated",
        {
            "players": players,
            "count": len(players),
            "online_users": online_users
        },
        to=room_code
    )

def get_online_users(socket_users, room_code):

    online_users = []

    for user in socket_users.values():

        if user["room_code"] == room_code:
            online_users.append(
                user["username"]
            )

    return online_users