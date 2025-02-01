from cocotst.app import Cocotst
from cocotst.event.message import GroupMessage
from cocotst.network.model.target import Target
from graia.saya.builtins.broadcast.shortcut import listen, dispatch
from dataclasses import dataclass
from typing import Dict, List, Optional
from cocotst.message.parser.msgsaw import Main, MessageSaw, QSubResult, Sub


@dataclass
class GameState:
    board: List[str]
    player1: str
    player2: Optional[str]
    current_turn: str
    is_started: bool
    piece1: str = "⭕"
    piece2: str = "❌"


games: Dict[str, GameState] = {}


def check_win(board: List[str]) -> bool:
    win_patterns = [
        [0, 1, 2],
        [3, 4, 5],
        [6, 7, 8],
        [0, 3, 6],
        [1, 4, 7],
        [2, 5, 8],
        [0, 4, 8],
        [2, 4, 6],
    ]
    return any(
        board[p[0]] != "□" and board[p[0]] == board[p[1]] == board[p[2]]
        for p in win_patterns
    )


def format_board(board: List[str]) -> str:
    return f"""当前棋盘:
{board[0]}|{board[1]}|{board[2]}
-+-+-
{board[3]}|{board[4]}|{board[5]}
-+-+-
{board[6]}|{board[7]}|{board[8]}"""


@listen(GroupMessage)
@dispatch(
    MessageSaw(
        Main(match="井", alt_match=["#"], need_argv=False),
        [
            Sub(match="开", alt_match=["start", "new"]),
            Sub(match="入", alt_match=["join", "in"]),
            Sub(
                match="落",
                alt_match=["put", "place"],
                need_argv=True,
                lack_argv_stop=False,
            ),
            Sub(match="退", alt_match=["quit", "exit"]),
            Sub(match="帮助", alt_match=["help", "?"]),
        ],
    )
)
async def handle_tictactoe(app: Cocotst, target: Target, result: QSubResult):
    user_id = target.target_unit

    # 显示帮助信息
    if result.is_pure_main or result.match_sub_command("帮助"):
        await app.send_group_message(
            target,
            content="""游戏指令:
/井开 (或 /井start) - 创建新游戏
/井入 (或 /井join) - 加入游戏
/井落 1-9 (或 /井put 1-9) - 在对应位置落子
/井退 (或 /井quit) - 结束游戏
/井帮助 (或 /井help, /井?) - 显示此帮助""",
        )
        return

    # 创建新游戏
    if result.match_sub_command("开"):
        if user_id in games:
            await app.send_group_message(target, content="已有一局游戏正在进行中!")
            return

        games[user_id] = GameState(
            board=["□"] * 9,
            player1=user_id,
            player2=None,
            current_turn=user_id,
            is_started=False,
        )
        await app.send_group_message(
            target,
            content="游戏创建成功! 等待玩家2加入...\n输入'/井入'或'/井join'即可加入",
        )

    # 加入游戏
    elif result.match_sub_command("入"):
        if user_id not in games:
            await app.send_group_message(target, content="当前没有等待加入的游戏!")
            return

        game = games[user_id]
        if game.is_started:
            await app.send_group_message(target, content="游戏已经开始了!")
            return

        if user_id == game.player1:
            await app.send_group_message(target, content="你已经是玩家1了!")
            return

        game.player2 = user_id
        game.is_started = True
        await app.send_group_message(
            target,
            content=f"玩家2加入成功!\n游戏开始!\n玩家1: {game.piece1}\n玩家2: {game.piece2}\n\n轮到玩家1行动\n输入'/井落 1-9'来下棋\n\n{format_board(game.board)}",
        )

    # 下棋
    elif result.match_sub_command("落"):
        if user_id not in games:
            await app.send_group_message(target, content="当前没有进行中的游戏!")
            return

        game = games[user_id]
        if not game.is_started:
            await app.send_group_message(target, content="游戏还没开始!")
            return

        if user_id != game.current_turn:
            await app.send_group_message(target, content="现在不是你的回合!")
            return

        try:
            position = int(result.sub_argv) - 1
            if not (0 <= position <= 8):
                raise ValueError()
        except ValueError:
            await app.send_group_message(target, content="请输入1-9的数字来选择位置!")
            return

        if game.board[position] != "□":
            await app.send_group_message(target, content="这个位置已经有棋子了!")
            return

        piece = game.piece1 if user_id == game.player1 else game.piece2
        game.board[position] = piece

        if check_win(game.board):
            await app.send_group_message(
                target,
                content=f"{format_board(game.board)}\n\n游戏结束! {'玩家1' if user_id == game.player1 else '玩家2'}获胜!",
            )
            del games[user_id]
            return

        if "□" not in game.board:
            await app.send_group_message(
                target, content=f"{format_board(game.board)}\n\n游戏结束! 平局!"
            )
            del games[user_id]
            return

        game.current_turn = game.player2 if user_id == game.player1 else game.player1
        await app.send_group_message(
            target,
            content=f"{format_board(game.board)}\n\n轮到{'玩家1' if game.current_turn == game.player1 else '玩家2'}行动",
        )

    # 退出游戏
    elif result.match_sub_command("退"):
        if user_id not in games:
            await app.send_group_message(target, content="当前没有进行中的游戏!")
            return

        game = games[user_id]
        if user_id not in [game.player1, game.player2]:
            await app.send_group_message(
                target, content="只有游戏中的玩家才能结束游戏!"
            )
            return

        del games[user_id]
        await app.send_group_message(target, content="游戏已结束!")
