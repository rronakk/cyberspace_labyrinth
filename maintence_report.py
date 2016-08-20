"""
Airtime labyrinth challenge:
Submitting maintenance report to mothership.
Finding all rooms with broken light, and writing on all lit rooms in sorted order.
"""
import requests
import json

_url = "http://challenge2.airtime.com:7182"
_headers = {"X-Labyrinth-Email": "knockronak@gmail.com"}


def get_writing(room):
    """Get the writing on the wall of a room.
    Args:
        room : Room ID of the labyrinth
    Returns:
        dictionary {order: writing}."""
    response = requests.get(_url + "/wall",
                            params={"roomId": room},
                            headers=_headers)
    body = json.loads(response.text)
    return {int(body['order']): body['writing']}


def get_neighbors(room):
    """Get the neighbors for a given room.
    Args:
        room : Room ID of the labyrinth.
    Returns:
        list of rooms in the neighborhood
    """
    neighbors = []
    response = requests.get(_url + "/exits", params={"roomId": room},
                            headers=_headers)
    exists = json.loads(response.text)["exits"]
    if not exists:
        return []
    for direction in exists:
        adj_room_response = requests.get(_url + "/move",
                                         params={"roomId": room,
                                                 "exit": direction},
                                         headers=_headers)
        neighbors.append(json.loads(adj_room_response.text)["roomId"])
    return neighbors


def main():
    """Run the search through the labyrinth
    """
    broken_rooms = []
    wall_writing = {}
    start_response = requests.get(_url + "/start",
                                  headers=_headers)
    start_room = json.loads(start_response.text)['roomId']
    # Do breadth-first search through the labyrinth.
    queue = [start_room]
    visited_rooms = {}
    while queue:
        curr_room = queue.pop(0)
        # keep track of visited room
        visited_rooms[curr_room] = True
        # Check writing and order on current wall
        if -1 in get_writing(curr_room).keys():
            broken_rooms.append(curr_room)
        else:
            # Keep track of {order:writing} dictionary.
            wall_writing.update(get_writing(curr_room))
        # Get new neighbors
        neighbors = get_neighbors(curr_room)
        for each_neighbor in neighbors:
            if each_neighbor not in visited_rooms:
                queue.append(each_neighbor)

    challenge_code = ''.join([value for (key, value) in sorted(wall_writing.items())])
    data = json.dumps({"roomIds": broken_rooms, "challenge": challenge_code})
    submit = requests.post(_url + "/report", data=data, headers=_headers)
    return submit.text

if __name__ == "__main__":
    print(main())
