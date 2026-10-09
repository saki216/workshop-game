"""アイドルファンサゲーム (tkinter 版)

遊び方:
    - 「ライブスタート！」ボタンを押すとゲームが始まります。
    - 客席からファンサを求める「うちわ」が掲げられます！
    - うちわをすばやくクリックして、たくさんのファンサを届けましょう！
    - 制限時間は 30 秒です。
"""

import math
import random
import tkinter as tk

# ---- 画面・ゲーム設定 ----
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 680
GAME_TIME = 30  # 制限時間（秒）

# ファンサのメッセージリスト
FANSA_MESSAGES = [
    ("ハート\nして💕", "#ff2d75"),
    ("ウインク\nして😉", "#ffe600"),
    ("指さして\n👉", "#00d2d3"),
    ("投げキス\nして😘", "#ff6b81"),
    ("ピース\nして✌", "#1dd1a1"),
    ("手を\n振って👋", "#ffa502"),
    ("バーン\nして🔫", "#ff4757"),
    ("エアハグ\nして🤗", "#ff9ff3"),
    ("大好き\n💖", "#e056fd"),
]

# カラーパレット
COLOR_BG = "#0d0a1a"          # ライブ会場の暗い客席背景
COLOR_HEADER = "#1a0826"      # ステージ上部
COLOR_PENLIGHTS = [
    "#ff4081", "#00e5ff", "#76ff03", "#ffd600",
    "#e040fb", "#ff6e40", "#69f0ae", "#40c4ff"
]


class IdolFansaGame:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("🎤 アイドルファンサゲーム ✨")
        self.root.resizable(False, False)

        # メインキャンバス
        self.canvas = tk.Canvas(
            root,
            width=WINDOW_WIDTH,
            height=WINDOW_HEIGHT,
            bg=COLOR_BG,
            highlightthickness=0
        )
        self.canvas.pack()

        # うちわの配置（3行 × 3列 = 9箇所）
        self.slots = []
        self._init_slot_positions()

        # ゲーム状態
        self.is_playing = False
        self.score = 0
        self.time_left = GAME_TIME
        self.timer_id = None
        self.spawn_timer_id = None

        # 各スロットのうちわ情報
        self.fans = []
        for i in range(9):
            self.fans.append({
                "state": "hidden",   # "hidden" | "up" | "hit"
                "tag": f"fan_{i}",
                "hide_id": None,
                "msg": "",
                "color": "#ffe600"
            })

        # イベント
        self.canvas.bind("<Button-1>", self.on_click)

        # 背景と初期画面
        self.draw_live_venue()
        self.show_start_screen()

    def _init_slot_positions(self) -> None:
        """客席のうちわ位置（3x3）の座標"""
        start_x = 120
        gap_x = 200
        start_y = 200
        gap_y = 145

        for row in range(3):
            for col in range(3):
                cx = start_x + col * gap_x
                cy = start_y + row * gap_y
                self.slots.append((cx, cy))

    def draw_live_venue(self) -> None:
        """ライブ会場の背景を描画（スポットライト・客席・ペンライト）"""
        self.canvas.delete("all")

        # 1. ステージ照明（上部からのスポットライト光線）
        spotlights = [
            (WINDOW_WIDTH * 0.15, 0, WINDOW_WIDTH * 0.05, WINDOW_HEIGHT, "#ff1493"),
            (WINDOW_WIDTH * 0.40, 0, WINDOW_WIDTH * 0.35, WINDOW_HEIGHT, "#7928ca"),
            (WINDOW_WIDTH * 0.60, 0, WINDOW_WIDTH * 0.65, WINDOW_HEIGHT, "#0070f3"),
            (WINDOW_WIDTH * 0.85, 0, WINDOW_WIDTH * 0.95, WINDOW_HEIGHT, "#00dfd8"),
        ]
        for sx, sy, ex, ey, col in spotlights:
            # 光線の扇形・多角形
            self.canvas.create_polygon(
                sx - 20, sy, sx + 20, sy,
                ex + 80, ey, ex - 80, ey,
                fill=col, outline="", stipple="gray25"
            )

        # 2. 客席のペンライト（無数のカラフルな光）
        random.seed(42)  # ペンライトの配置を固定
        for _ in range(120):
            px = random.randint(15, WINDOW_WIDTH - 15)
            py = random.randint(120, WINDOW_HEIGHT - 20)
            col = random.choice(COLOR_PENLIGHTS)
            angle = random.randint(-25, 25)
            # ペンライトの棒と光
            rad = math.radians(angle)
            lx2 = px + 14 * math.sin(rad)
            ly2 = py - 14 * math.cos(rad)
            self.canvas.create_line(px, py, lx2, ly2, fill=col, width=3, capstyle="round")
            # ペンライトの先端の輝き
            self.canvas.create_oval(lx2 - 2, ly2 - 2, lx2 + 2, ly2 + 2, fill="#ffffff", outline="")

        # 3. 観客のシルエット（客席の雰囲気）
        for _ in range(40):
            cx = random.randint(20, WINDOW_WIDTH - 20)
            cy = random.randint(140, WINDOW_HEIGHT - 10)
            r = random.randint(14, 22)
            self.canvas.create_oval(
                cx - r, cy - r, cx + r, cy + r,
                fill="#07040d", outline=""
            )
        random.seed()  # ランダムシード解除

        # 4. 各座席ブロックの足場（目印）
        for cx, cy in self.slots:
            self.canvas.create_oval(
                cx - 65, cy + 30, cx + 65, cy + 50,
                fill="#05030a", outline="#231738", width=1
            )

        # 5. 上部ヘッダー（ライブステージバー）
        self.canvas.create_rectangle(
            0, 0, WINDOW_WIDTH, 85,
            fill=COLOR_HEADER, outline="#ff2d75", width=2
        )

        # ヘッダーテキスト
        self.canvas.create_text(
            15, 25, anchor="w",
            text="🎤 LIVE STAGE",
            fill="#ff77a9",
            font=("Meiryo", 13, "bold")
        )
        self.canvas.create_text(
            15, 55, anchor="w",
            text="✨ ファンサバトル！",
            fill="#ffffff",
            font=("Meiryo", 16, "bold")
        )
        self.time_text = self.canvas.create_text(
            370, 42, anchor="center",
            text=f"残り時間: {self.time_left}秒",
            fill="#ffffff",
            font=("Meiryo", 16, "bold")
        )
        self.score_text = self.canvas.create_text(
            530, 42, anchor="center",
            text=f"ファンサ: {self.score}回",
            fill="#ffe600",
            font=("Meiryo", 17, "bold")
        )

    def show_start_screen(self) -> None:
        """スタート画面（ゲーム開始前）"""
        self.overlay_tag = "start_overlay"

        # ポップアップパネル
        self.canvas.create_rectangle(
            60, 110, WINDOW_WIDTH - 60, 580,
            fill="#160d29", outline="#ff2d75", width=4,
            tags=self.overlay_tag
        )

        # タイトル & 説明
        self.canvas.create_text(
            WINDOW_WIDTH / 2, 160,
            text="💖 アイドルファンサゲーム 💖",
            fill="#ff77a9",
            font=("Meiryo", 22, "bold"),
            tags=self.overlay_tag
        )
        self.canvas.create_text(
            WINDOW_WIDTH / 2, 220,
            text="あなたは今、満員のライブステージに立っています！\n客席から次々と掲げられる「うちわ」を見つけて、\nクリックでファンサ（ハート・投げキッス等）を届けよう！\n\n制限時間は 30 秒です！",
            fill="#f8f9fa",
            font=("Meiryo", 12),
            justify="center",
            tags=self.overlay_tag
        )

        # うちわの見本を中央に描画
        sample_cx = WINDOW_WIDTH / 2
        sample_cy = 380
        self.draw_uchiwa_at(sample_cx, sample_cy, "ハート\nして💕", "#ff2d75", tag=self.overlay_tag, is_hit=False)

        # スタートボタン
        self._create_button(
            WINDOW_WIDTH / 2, 510,
            text="ライブスタート！🎤",
            command=self.start_game,
            tags=self.overlay_tag,
            btn_color="#ff2d75",
            hover_color="#e01058"
        )

    def _create_button(
        self, cx: float, cy: float, text: str, command, tags: str,
        btn_color="#ff2d75", hover_color="#e01058"
    ) -> None:
        """可愛いボタンの作成"""
        w, h = 220, 52
        x1, y1 = cx - w / 2, cy - h / 2
        x2, y2 = cx + w / 2, cy + h / 2

        btn_bg = self.canvas.create_rectangle(
            x1, y1, x2, y2,
            fill=btn_color, outline="#ffffff", width=2,
            tags=(tags, "btn")
        )
        btn_txt = self.canvas.create_text(
            cx, cy,
            text=text,
            fill="#ffffff",
            font=("Meiryo", 15, "bold"),
            tags=(tags, "btn")
        )

        def on_enter(e):
            self.canvas.itemconfig(btn_bg, fill=hover_color)
        def on_leave(e):
            self.canvas.itemconfig(btn_bg, fill=btn_color)
        def on_press(e):
            command()

        for item in (btn_bg, btn_txt):
            self.canvas.tag_bind(item, "<Enter>", on_enter)
            self.canvas.tag_bind(item, "<Leave>", on_leave)
            self.canvas.tag_bind(item, "<Button-1>", on_press)

    def start_game(self) -> None:
        """ゲーム開始"""
        self.canvas.delete("start_overlay")
        self.canvas.delete("gameover_overlay")

        self.is_playing = True
        self.score = 0
        self.time_left = GAME_TIME

        for fan in self.fans:
            self._hide_fan(fan)

        self.update_hud()
        self.tick_timer()
        self.spawn_fan_loop()

    def update_hud(self) -> None:
        """HUD表示更新"""
        self.canvas.itemconfig(self.score_text, text=f"ファンサ: {self.score}回")
        color = "#ff3838" if self.time_left <= 5 else "#ffffff"
        self.canvas.itemconfig(self.time_text, text=f"残り時間: {self.time_left}秒", fill=color)

    def tick_timer(self) -> None:
        """1秒ごとのカウントダウン"""
        if not self.is_playing:
            return

        self.update_hud()

        if self.time_left <= 0:
            self.game_over()
            return

        self.time_left -= 1
        self.timer_id = self.root.after(1000, self.tick_timer)

    def spawn_fan_loop(self) -> None:
        """客席からうちわが掲げられるループ"""
        if not self.is_playing:
            return

        hidden_indices = [i for i, f in enumerate(self.fans) if f["state"] == "hidden"]
        if hidden_indices:
            num_to_spawn = 1
            if len(hidden_indices) >= 3 and random.random() < 0.4:
                num_to_spawn = 2

            chosen = random.sample(hidden_indices, min(num_to_spawn, len(hidden_indices)))
            for idx in chosen:
                self.pop_up_fan(idx)

        # 残り時間に応じて出現スピードがアップ
        if self.time_left > 20:
            delay = random.randint(700, 1050)
        elif self.time_left > 10:
            delay = random.randint(550, 850)
        else:
            delay = random.randint(400, 680)

        self.spawn_timer_id = self.root.after(delay, self.spawn_fan_loop)

    def pop_up_fan(self, index: int) -> None:
        """指定位置にうちわを掲げる"""
        fan = self.fans[index]
        fan["state"] = "up"

        # ランダムなファンサ文言とカラーを割り当て
        msg, color = random.choice(FANSA_MESSAGES)
        fan["msg"] = msg
        fan["color"] = color

        cx, cy = self.slots[index]
        self.draw_uchiwa_at(cx, cy, msg, color, tag=fan["tag"], is_hit=False)

        # 出ている時間（時間経過で客席に下ろす）
        stay_time = max(650, int(1150 - (GAME_TIME - self.time_left) * 16))
        fan["hide_id"] = self.root.after(stay_time, lambda: self._on_fan_timeout(index))

    def _on_fan_timeout(self, index: int) -> None:
        """ファンサをもらえずうちわを下ろす"""
        fan = self.fans[index]
        if fan["state"] == "up":
            self._hide_fan(fan)

    def _hide_fan(self, fan: dict) -> None:
        """うちわを引っ込める"""
        if fan["hide_id"] is not None:
            self.root.after_cancel(fan["hide_id"])
            fan["hide_id"] = None
        self.canvas.delete(fan["tag"])
        fan["state"] = "hidden"

    def draw_uchiwa_at(
        self, cx: float, cy: float, msg: str, border_color: str,
        tag: str, is_hit: bool = False
    ) -> None:
        """うちわを描画する（コンサート用うちわ風）"""
        self.canvas.delete(tag)

        # うちわの中心位置（穴位置より少し上）
        uy = cy - 25
        r = 46  # うちわの半径

        # 1. 持ち手（柄）
        self.canvas.create_rectangle(
            cx - 5, uy + r - 4, cx + 5, uy + r + 38,
            fill="#f5f5f5", outline="#9e9e9e", width=1, tags=tag
        )
        # 持ち手の穴
        self.canvas.create_oval(
            cx - 3, uy + r + 26, cx + 3, uy + r + 34,
            fill="#0d0a1a", outline="#9e9e9e", width=1, tags=tag
        )

        if is_hit:
            # ファンサを受けた時のハッピーエフェクト（ピンクオーラ）
            self.canvas.create_oval(
                cx - (r + 10), uy - (r + 10), cx + (r + 10), uy + (r + 10),
                fill="", outline="#ff69b4", width=4, tags=tag
            )

        # 2. うちわのフチ（蛍光モール風の華やかな外枠）
        self.canvas.create_oval(
            cx - (r + 4), uy - (r + 4), cx + (r + 4), uy + (r + 4),
            fill=border_color, outline="#ffffff", width=2, tags=tag
        )

        # 3. うちわの盤面（黒色ベース）
        self.canvas.create_oval(
            cx - r, uy - r, cx + r, uy + r,
            fill="#121212", outline="", tags=tag
        )

        if is_hit:
            # ファンサ成功時のメッセージ
            self.canvas.create_text(
                cx, uy - 4,
                text="きゃー!!\n💕昇天💕",
                fill="#ff2d75",
                font=("Meiryo", 13, "bold"),
                justify="center",
                tags=tag
            )
            # キラキラハート
            self.canvas.create_text(
                cx - 32, uy - 32, text="💖", font=("Meiryo", 14), tags=tag
            )
            self.canvas.create_text(
                cx + 32, uy - 32, text="✨", font=("Meiryo", 14), tags=tag
            )
        else:
            # 4. ファンサを求める文字（黄色・ピンクなどの蛍光デコ文字風）
            # 影（立体フチ取り）
            self.canvas.create_text(
                cx + 1, uy + 1,
                text=msg,
                fill="#000000",
                font=("Meiryo", 12, "bold"),
                justify="center",
                tags=tag
            )
            # 本文
            self.canvas.create_text(
                cx, uy,
                text=msg,
                fill=border_color if border_color != "#121212" else "#ffe600",
                font=("Meiryo", 12, "bold"),
                justify="center",
                tags=tag
            )

    def on_click(self, event) -> None:
        """キャンバスクリック（ファンサを返す）判定"""
        if not self.is_playing:
            return

        mx, my = event.x, event.y

        for i, fan in enumerate(self.fans):
            if fan["state"] != "up":
                continue

            cx, cy = self.slots[i]
            uy = cy - 25
            # うちわの中心 (cx, uy) からの距離判定
            dist = math.hypot(mx - cx, my - uy)

            if dist < 52:
                self.fansa_hit(i, mx, my)
                break

    def fansa_hit(self, index: int, hit_x: float, hit_y: float) -> None:
        """うちわにファンサを返した時の演出"""
        fan = self.fans[index]
        fan["state"] = "hit"

        if fan["hide_id"] is not None:
            self.root.after_cancel(fan["hide_id"])
            fan["hide_id"] = None

        # スコア加算
        self.score += 1
        self.update_hud()

        # 喜びのうちわを描画
        cx, cy = self.slots[index]
        self.draw_uchiwa_at(cx, cy, fan["msg"], fan["color"], tag=fan["tag"], is_hit=True)

        # ファンサエフェクト（フワッと上がるハート & テキスト）
        self.show_fansa_effect(cx, cy - 65)

        # 歓喜の後、350msで引っ込む
        fan["hide_id"] = self.root.after(350, lambda: self._hide_fan(fan))

    def show_fansa_effect(self, x: float, y: float) -> None:
        """ファンサ時のポップアップ演出"""
        effect_tag = f"eff_{random.randint(1000, 9999)}"
        words = ["FANSA! 💖", "KISS! 💋", "LOVE! 💕", "THANKS! ✨"]
        chosen_word = random.choice(words)

        txt = self.canvas.create_text(
            x, y,
            text=chosen_word,
            fill="#ff77a9",
            font=("Meiryo", 14, "bold"),
            tags=effect_tag
        )

        def float_up(step: int):
            if step > 6:
                self.canvas.delete(effect_tag)
                return
            self.canvas.move(txt, 0, -3)
            self.root.after(40, lambda: float_up(step + 1))

        float_up(0)

    def game_over(self) -> None:
        """ゲーム終了（ライブ終了）"""
        self.is_playing = False

        if self.timer_id is not None:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
        if self.spawn_timer_id is not None:
            self.root.after_cancel(self.spawn_timer_id)
            self.spawn_timer_id = None

        for fan in self.fans:
            self._hide_fan(fan)

        self.show_game_over_screen()

    def show_game_over_screen(self) -> None:
        """ライブ終了リザルト画面"""
        self.overlay_tag = "gameover_overlay"

        # 背景パネル
        self.canvas.create_rectangle(
            60, 110, WINDOW_WIDTH - 60, 580,
            fill="#160d29", outline="#ff2d75", width=4,
            tags=self.overlay_tag
        )

        # ライブ終了
        self.canvas.create_text(
            WINDOW_WIDTH / 2, 170,
            text="🎉 ライブ終了！ アンコール！ 🎉",
            fill="#ff77a9",
            font=("Meiryo", 20, "bold"),
            tags=self.overlay_tag
        )

        # 届けたファンサ数
        self.canvas.create_text(
            WINDOW_WIDTH / 2, 235,
            text=f"ファンサを届けた回数: {self.score} 人！",
            fill="#ffffff",
            font=("Meiryo", 22, "bold"),
            tags=self.overlay_tag
        )

        # アイドルランク評価
        if self.score >= 26:
            rank_title = "👑 称号: 伝説のドーム級トップアイドル！"
            rank_desc = "神ファンサ連発！\n会場中のファン全員のハートを完全に射抜きました！💘✨"
            rank_color = "#ffd700"
        elif self.score >= 18:
            rank_title = "🌟 称号: 大人気スーパースター！"
            rank_desc = "圧倒的なファンサ対応！\n客席は黄色い大歓声に包まれています！💖"
            rank_color = "#ff4081"
        elif self.score >= 10:
            rank_title = "✨ 称号: キラキラ輝く注目アイドル！"
            rank_desc = "ナイスファンサ！\nたくさんのファンに笑顔と幸せを届けました！😊"
            rank_color = "#00e5ff"
        else:
            rank_title = "🌱 称号: デビューしたての新星アイドル！"
            rank_desc = "初ライブお疲れ様！\n次のステージではもっとたくさんのファンサを届けよう！🎤"
            rank_color = "#b0bec5"

        self.canvas.create_text(
            WINDOW_WIDTH / 2, 310,
            text=rank_title,
            fill=rank_color,
            font=("Meiryo", 15, "bold"),
            tags=self.overlay_tag
        )
        self.canvas.create_text(
            WINDOW_WIDTH / 2, 375,
            text=rank_desc,
            fill="#f5f5f5",
            font=("Meiryo", 13),
            justify="center",
            tags=self.overlay_tag
        )

        # もう一度遊ぶボタン
        self._create_button(
            WINDOW_WIDTH / 2, 490,
            text="次のライブへ！🎤",
            command=self.start_game,
            tags=self.overlay_tag,
            btn_color="#ff2d75",
            hover_color="#e01058"
        )


def main() -> None:
    root = tk.Tk()
    IdolFansaGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()
