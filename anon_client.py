from asyncio import new_event_loop
from threading import Thread
from uuid import uuid4
from .anon_http import AnonHTTP
from .rocket_http import RocketHTTP
from .models import AccountInfo
from .models import Post
from .models import Comment
from .models import User
from .models import UserSuggestion
from .paginated_list import PaginatedList
from .models.contents import TextContents
from .models.contents import TextContentsData
from .ws import *
from .utils import *


FILTER_MY_SUBSCRIPTIONS = "MY_SUBSCRIPTIONS"
FILTER_TOP = "TOP"
FILTER_AUDIO = "AUDIO"
FILTER_NEWEST = "NEWEST"
PERIOD_LAST_DAY = "LAST_DAY"
PERIOD_LAST_WEEK = "LAST_WEEK"
PERIOD_LAST_MONTH = "LAST_MONTH"
PERIOD_LAST_YEAR = "LAST_YEAR"
MESSAGE_TYPE_USER_JOIN = "uj"
MESSAGE_TYPE_USER_LEAVE = "ul"
MESSAGE_TYPE_DELETED = "rm"
MESSAGE_TYPE_USER_KICKED = "ru"


class AnonClient:
    """
    The main class used to interact with Anon
    """

    def __init__(self,
                 connect_websocket: bool = True,
                 prefix: str = "",
                 proxy: Optional[str] = None,
                 ws_debug: bool = False) -> None:
        self._anon_http = AnonHTTP()
        self._rocket_http = RocketHTTP()
        self.token = None
        self.rocket_token = None
        self.rocket_id = None
        self.current_account_info = None
        self.listener = None
        self._handlers = []
        self.connect = connect_websocket
        self.prefix = prefix
        self.ws_debug = ws_debug

    def _set_account(self, info: AccountInfo) -> None:
        self.token = info.token
        self.rocket_token = info.rocket_token
        self.rocket_id = info.rocket_id
        self._anon_http.headers["Authorization"] = self.token
        self._rocket_http.headers["X-Auth-Token"] = self.rocket_token
        self._rocket_http.headers["X-User-Id"] = self.rocket_id
        self.current_account_info = info

    def _forget_account(self) -> None:
        self.token = None
        self.rocket_token = None
        self.rocket_id = None
        self.current_account_info = None
        del self._anon_http.headers["Authorization"]
        del self._rocket_http.headers["X-Auth-Token"]
        del self._rocket_http.headers["X-User-Id"]

    async def _create_connection(self, info: AccountInfo):
        lp = new_event_loop()
        self.listener = WebSocketListener(info.rocket_id, info.rocket_token, lp, self.ws_debug)
        Thread(target=lp.run_forever).start()
        lp.create_task(self.listener.start())
        for handler in self._handlers: self.listener.add_event_handler(handler)

    async def _get_rocket_token(self, login: str, password: str) -> str:
        data = {"username": login, "password": password}
        return (await self._rocket_http.call_post_json("login", data)).json()["data"]["authToken"]

    async def generate_nicknames(self) -> list:
        """
        Generates list of recommended nicknames
        :return: list of generated nicknames
        """
        return (await self._anon_http.call_post_json("/users/generate", [])).json()["data"]

    async def nickname_to_username(self, nickname: str) -> str:
        """
        Generates a unique username from a non-unique nickname
        :param nickname: non-unique nickname
        :return: unique username
        """
        return (await self._anon_http.call_post_json("/auth/register/generate", {"name": nickname})).json()["data"]

    async def register(
            self,
            login: str,
            nickname: str,
            password: str,
            invite_code: Optional[str] = None,
            change_account: bool = True
    ) -> AccountInfo:
        """
        Attempts to create a new account,
        if successful,
        returns account information and changes cookies if the change_account parameter is True
        :param login: account login
        :param nickname: account nickname
        :param password: account password
        :param invite_code: invitation code, one-time accrues coins to the account
        :param change_account: is it required to change cookies
        :return: AccountInfo object
        """
        data = {"login": login, "name": nickname, "password": password}
        if invite_code is not None: data["inviteCode"] = invite_code
        info = AccountInfo.from_dict(
            (await self._anon_http.call_post_json("/auth/register", data)).json()["data"]
        )
        info.rocket_token = await self._get_rocket_token(info.login, info.rocket_key)
        if change_account: self._set_account(info)
        if self.connect: await self._create_connection(info)
        return info

    async def login(self, login: str, password: str, change_account: bool = True) -> AccountInfo:
        """
        Attempts to log in to the account,
        if successful,
        returns account information and changes cookies if the change_account parameter is True
        :param login: account login
        :param password: account password
        :param change_account: is it required to change cookies
        :return: AccountInfo object
        """
        data = {"login": login, "password": password}
        info = AccountInfo.from_dict(
            (await self._anon_http.call_post_json("/auth/login", data)).json()["data"]
        )
        info.rocket_token = await self._get_rocket_token(info.login, info.rocket_key)
        if change_account: self._set_account(info)
        if self.connect: await self._create_connection(info)
        return info

    async def logout(self):
        """
        Logs out of the account and deletes all authorization cookies
        """
        await self._anon_http.call_post_json("/auth/logout", [])
        if self.listener is not None: self.listener.stop()
        self._forget_account()

    async def view_posts(self, post_ids: list[str]):
        """
        Makes each post from the list viewed by you
        :param post_ids: list of post ids
        """
        await self._anon_http.call_post_json("/posts/v1/posts/views", {"ids": post_ids})

    async def view_post(self, post_id: str):
        """
        Makes post viewed by you
        :param post_id: id of the post
        """
        await self.view_posts([post_id])

    async def get_post(self, post_id: str) -> Post:
        """
        Gets information about the post using the post id
        :param post_id: id of the post
        :return: Post object
        """
        pid = post_id if post_id.startswith("p:") else f"p:{post_id}"
        return Post.from_dict(
            (await self._anon_http.call_get(f"/posts/v1/posts/{pid}")).json()["data"]
        )

    async def get_posts(self,
                        search_filter: str,
                        size: int,
                        period_of_time: Optional[str] = None,
                        after: Optional[str] = None) -> list[Post]:
        """
        Gets a list of posts in the global feed
        :param search_filter: filter by which posts will be selected
        :param size: maximum list size
        :param period_of_time: The time period used when searching for popular posts
        :param after: page cursor
        :return: list of the posts with "cursor" attribute
        """
        params = {"filter": search_filter, "first": size}
        if period_of_time is not None: params["periodOfTime"] = period_of_time
        if after is not None: params["after"] = after
        response = (await self._anon_http.call_get("/posts/v1/main", params)).json()["data"]
        return PaginatedList(
            response.get("cursor"),
            [Post.from_dict(post) for post in response["items"]]
        )

    async def get_user_posts(
            self,
            user_id: str,
            size: int,
            order_by: Optional[str] = "createdAt",
            after: Optional[str] = None
    ) -> list[Post]:
        """
        Gets a list of posts in the user profile
        :param user_id: id of the user
        :param size: maximum list size
        :param order_by: sorting method
        :param after: page tokene
        :return: list of the posts with "cursor" attribute
        """
        params = {"first": size}
        if order_by is not None: params["orderBy"] = order_by
        if after is not None: params["after"] = after
        response = (await self._anon_http.call_get(f"/posts/v1/profiles/{user_id}/posts", params)).json()["data"]
        return PaginatedList(
            response.get("cursor"),
            [Post.from_dict(post) for post in response["items"]]
        )

    async def get_post_comments(self, post_id: str, size: int, after: Optional[str] = None):
        """
        Gets a list of comments on the post
        :param post_id: id of the post
        :param size: maximum list size
        :param after: page cursor
        :return: list of the comments with "cursor" attribute
        """
        params = {"first": size}
        if after is not None: params["after"] = after
        pid = post_id if post_id.startswith("p:") else f"p:{post_id}"
        response = (await self._anon_http.call_get(f"/posts/v1/posts/{pid}/comments", params)).json()["data"]
        return PaginatedList(
            response.get("nextPageCursor"),
            [Comment.from_dict(comment) for comment in response["comments"]]
        )

    async def create_comment(self, parent_id: str, content: str, is_author_hidden: bool = False) -> Comment:
        """
        Creates a new comment
        :param parent_id: post id or comment id
        :param content: content of the comment
        :param is_author_hidden: is it required to hide author
        :return: Comment object
        """
        pid = parent_id if parent_id.startswith("p:") else f"p:{parent_id}"
        response = await self._anon_http.call_post_json(
            "/posts/v1/comments",
            {
                "contents": [TextContents("TEXT", TextContentsData(content)).to_dict()],
                "isAuthorHidden": is_author_hidden,
                "parentId": pid
            }
        )
        return Comment.from_dict(response.json()["data"]["comment"])

    async def delete_comment(self, comment_id: str, block_author: bool = False, only_for_me: bool = True):
        """
        Deletes or hides a comment
        :param comment_id: id of the comment
        :param block_author: is it required to block the author
        :param only_for_me: deletes the comment if False, hides the comment if True
        """
        cid = comment_id if comment_id.startswith("p:") else f"p:{comment_id}"
        params = {"blockAuthor": block_author, "onlyForMe": only_for_me}
        await self._anon_http.call_delete(f"/posts/v1/comments/{cid}", params)

    async def edit_comment(self, comment_id: str, content: str) -> Comment:
        """
        Edits a comment
        :param comment_id: id of the comment
        :param content: new content of the comment
        :return: Comment object
        """
        cid = comment_id if comment_id.startswith("p:") else f"p:{comment_id}"
        response = await self._anon_http.call_post_json(
            f"/posts/v1/comments/{cid}",
            {
                # this value does not affect anything, but the request does not work without it
                "author": {"profile": {"premiumFeatures": {"voicesAvailable": 0.0}}},
                "contents": [TextContents("TEXT", TextContentsData(content)).to_dict()]
            }
        )
        return Comment.from_dict(response.json()["data"])

    async def restore_comment(self, comment_id: str, unlock_author: bool = False):
        """
        Restores a hidden comment
        :param comment_id: id of the comment
        :param unlock_author: is it required to unlock the author
        :return:
        """
        cid = comment_id if comment_id.startswith("p:") else f"p:{comment_id}"
        params = {"unlockAuthor": unlock_author}
        await self._anon_http.call_delete(f"/posts/v1/comments/{cid}/restore", params)

    async def get_user(self, user_id: str) -> User:
        """
        Gets information about the user using the user id
        :param user_id: id of the user
        :return: User object
        """
        return User.from_dict(
            (await self._anon_http.call_get(f"/users/{user_id}")).json()["data"]
        )

    async def get_me(self) -> User:
        """
        Gets information about the current user
        :return: User object
        """
        return await self.get_user("me")

    async def send_chat_request(self, user_id: str, greeting: str):
        """
        Sends a request to the user to create a chat
        :param user_id: id of the user
        :param greeting: the message that the user will see
        """
        data = {"greeting": greeting}
        await self._anon_http.call_post_json(f"/users/{user_id}/chat-request", data)

    async def get_chat_online_users(self) -> list[UserSuggestion]:
        """
        Gets a (probably incomplete) list of online users in the messenger
        :return: Suggested users list
        """
        suggestions = (await self._anon_http.call_get("/users/cards/chat-online")).json()["data"]["items"]
        return [UserSuggestion.from_dict(suggestion) for suggestion in suggestions]

    async def edit_profile(self,
                           name: Optional[str] = None,
                           tagline: Optional[str] = None,
                           hide_profile: Optional[bool] = None,
                           allow_new_subscribes: Optional[bool] = None,
                           show_subscribers: Optional[bool] = None,
                           show_subscriptions: Optional[bool] = None,
                           is_messaging_allowed: Optional[bool] = None):
        """
        Edits a profile of current user
        :param name: new name
        :param tagline: new tagline
        :param hide_profile: is it required to hide profile
        :param allow_new_subscribes: is it required to hide profile
        :param show_subscribers: is it required to show user subscribers
        :param show_subscriptions: is it required to show user subscriptions
        :param is_messaging_allowed: is it required to accept private messages from other users
        :return: User object
        """
        data = {}
        if name is not None: data["name"] = name
        else: data["name"] = (await self.get_me()).name
        if tagline is not None: data["tagline"] = tagline
        if hide_profile is not None: data["isHidden"] = hide_profile
        if allow_new_subscribes is not None: data["allowNewSubscribers"] = allow_new_subscribes
        if show_subscribers is not None: data["showSubscribers"] = show_subscribers
        if show_subscriptions is not None: data["showSubscriptions"] = show_subscriptions
        if is_messaging_allowed is not None: data["isMessagingAllowed"] = is_messaging_allowed
        return User.from_dict(
            (await self._anon_http.call_patch_json("/users/me", data)).json()["data"]
        )

    async def send_message(self, room_id: str, text: str, message_type: Optional[str] = None) -> ChatMessage:
        """
        Sends a message to a chat
        :param room_id: id of the room
        :param text: text of the message
        :param message_type: type of the message
        :return: ChatMessage object
        """
        data = {
            "message": {
                "_id": "".join([f"{str(uuid4())}" + "-" if i != 5 else "" for i in range(6)]),
                "rid": room_id,
                "msg": text
            }
        }
        if message_type is not None: data["message"]["t"] = message_type
        return ChatMessage.from_dict(
            (await self._rocket_http.call_post_json("v1/chat.sendMessage", data)).json()["message"]
        )

    async def edit_message(self, room_id: str, message_id: str, new_content: str) -> ChatMessage:
        """
        Edits a message
        :param room_id: id of the room
        :param message_id: id of the message
        :param new_content: new message content
        :return: ChatMessage object
        """
        data = {"roomId": room_id, "msgId": message_id, "text": new_content}
        return ChatMessage.from_dict(
            (await self._rocket_http.call_post_json("v1/chat.update", data)).json()["mesage"]
        )

    async def delete_message(self, room_id: str, message_id: str, as_user: bool = True):
        """
        Deletes a message
        :param room_id: id of the room
        :param message_id: id of the message
        :param as_user: is it required to delete message as user
        """
        data = {"roomId": room_id, "msgId": message_id, "asUser": as_user}
        await self._rocket_http.call_post_json("v1/chat.delete", data)

    async def join_room(self, room_id: str):
        """
        Joins to a room
        :param room_id: id of the room
        """
        data = {"roomId": room_id}
        await self._rocket_http.call_post_json("v1/channels.join", data)

    async def leave_room(self, room_id: str):
        """
        Leaves from a room
        :param room_id: id of the room
        """
        data = {"roomId": room_id}
        await self._rocket_http.call_post_json("v1/channels.leave", data)

    async def subscribe(self, user_id: str):
        """
        Subscribes to the user
        :param user_id: id of the user
        """
        await self._anon_http.call_post_json(f"/users/{user_id}/subscription", [])

    async def unsubscribe(self, user_id: str):
        """
        Unsubscribes from the user
        :param user_id: id of the user
        """
        await self._anon_http.call_delete(f"/users/{user_id}/subscription", None)

    async def get_invite_code(self) -> str:
        """
        Gets a code to invite other users (used in the link https://app.anonymous.network/code
        :return: invite code
        """
        return (await self._anon_http.call_post("/users/invite", bytes())).json()["data"]["code"]

    def add_event_handler(self,
                          cli,
                          name: str,
                          handler: Callable,
                          payload_filter: Optional[Callable],
                          event_type: Optional[str] = None):
        handler = WebSocketListener.create_event_handler(cli, name, handler, payload_filter, event_type)
        if self.listener is None: self._handlers.append(handler)
        else: self.listener.add_event_handler(handler)

    def on_chat_message(self, payload_filter: Optional[Callable] = None):
        def register(handler: Callable):
            self.add_event_handler(
                self,
                EVENT_NAME_ROOMS_CHANGED,
                handler,
                payload_filter,
                EVENT_TYPE_MESSAGE_RECEIVED
            )
            return handler
        return register

    def on_command(self, commands: Union[str, list], prefix: Optional[str] = None):
        def register(handler: Callable):
            if isinstance(commands, str): cmds = [commands]
            else: cmds = commands
            for command in cmds:
                txt = f"{prefix if prefix is not None else self.prefix}{command}"
                reg = self.on_chat_message(lambda m: m.text.startswith(txt))
                reg(handler)
            return handler
        return register

    def on_notification(self, payload_filter: Optional[Callable] = None):
        def register(handler: Callable):
            self.add_event_handler(
                self,
                EVENT_NAME_NOTIFICATION,
                handler,
                payload_filter,
                None
            )
            return handler
        return register
