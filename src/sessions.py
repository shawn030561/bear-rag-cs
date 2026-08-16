"""会话存储：维护多轮对话上下文。

当前为进程内 dict，单机 Demo 够用；生产环境应替换为 Redis，
以 session_id 为 key 存 Conversation 的 JSON 快照，支持水平扩展。
"""
from conversation import Conversation


class SessionStore:
    def __init__(self, max_sessions: int = 10000):
        self._sessions: dict[str, Conversation] = {}
        self.max_sessions = max_sessions

    def get_or_create(self, session_id: str) -> Conversation:
        conv = self._sessions.get(session_id)
        if conv is None:
            if len(self._sessions) >= self.max_sessions:
                # 简单兜底：满员时淘汰最早会话，避免内存无限增长
                self._sessions.pop(next(iter(self._sessions)))
            conv = Conversation()
            self._sessions[session_id] = conv
        return conv
