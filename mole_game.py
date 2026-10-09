"""もぐらたたきゲーム (tkinter 版)

遊び方:
    - 「スタート」ボタンを押すとゲームが始まります。
    - 穴から出てきたモグラをクリック（タップ）して叩きましょう！
    - 制限時間は 30 秒です。時間内にたくさんのモグラを叩いてハイスコアを目指そう！
"""

import math
import random
import tkinter as tk

# ---- 画面・ゲーム設定 ----
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 650
GAME_TIME = 30  # 制限時間（秒）

# カラーパレット
COLOR_BG = "#78c850"         # 芝生の緑
COLOR_HEADER = "#2e7d32"     # ヘッダーの濃い緑
COLOR_HOLE_OUTER = "#5d4037" # 穴のフチ（土）
COLOR_HOLE_INNER = "#271c19" # 穴の奥（暗い土）
COLOR_MOLE = "#8d5b4c"       # モグラの体
COLOR_MOLE_BELLY = "#d7ccc8" # モグラの口元
COLOR_NOSE = "#ff8a80"       # モグラの鼻
COLOR_STAR = "#ffd54f"       # ヒット時の星
COLOR_BTN = "#ff9800"        # ボタンのオレンジ
COLOR_BTN_HOVER = "#f57c00"

class MoleGame:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("もぐらたたきゲーム")
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

        # 穴の配置設定（3行 × 3列 = 9個）
        self.holes = []
        self._init_hole_positions()

        # ゲーム状態
        self.is_playing = False
        self.score = 0
        self.time_left = GAME_TIME
        self.timer_id = None
        self.spawn_timer_id = None

        # 各穴のモグラ情報: {"state": "hidden"|"up"|"hit", "tag": str, "hide_id": str}
        self.moles = []
        for i in range(9):
            self.moles.append({
                "state": "hidden",
                "tag": f"mole_{i}",
                "hide_id": None
            })

        # イベントバインド
        self.canvas.bind("<Button-1>", self.on_click)

        # 穴と初期UIを描画
        self.draw_field()
        self.show_start_screen()

    def _init_hole_positions(self) -> None:
        """3x3 の穴の中心座標を計算"""
        start_x = 110
        gap_x = 190
        start_y = 190
        gap_y = 135

        for row in range(3):
            for col in range(3):
                cx = start_x + col * gap_x
                cy = start_y + row * gap_y
                self.holes.append((cx, cy))

    def draw_field(self) -> None:
        """背景・ヘッダー・穴を描画"""
        self.canvas.delete("all")

        # 上部ヘッダー帯
        self.canvas.create_rectangle(
            0, 0, WINDOW_WIDTH, 90,
            fill=COLOR_HEADER, outline=""
        )

        # ヘッダーテキスト
        self.canvas.create_text(
            15, 30, anchor="w",
            text="🔨 もぐらたたき",
            fill="#ffffff",
            font=("Meiryo", 18, "bold")
        )
        self.time_text = self.canvas.create_text(
            350, 45, anchor="center",
            text=f"残り時間: {self.time_left}秒",
            fill="#ffffff",
            font=("Meiryo", 16, "bold")
        )
        self.score_text = self.canvas.create_text(
            510, 45, anchor="center",
            text=f"スコア: {self.score}",
            fill="#ffeb3b",
            font=("Meiryo", 18, "bold")
        )

        # 芝生の装飾（小さな草の房）
        grass_positions = [
            (40, 120), (550, 140), (280, 120),
            (30, 270), (560, 280), (25, 430),
            (570, 450), (180, 560), (420, 560)
        ]
        for gx, gy in grass_positions:
            self._draw_grass(gx, gy)

        # 穴の描画（9箇所）
        for i, (cx, cy) in enumerate(self.holes):
            # 穴の外枠（盛り上がった土）
            self.canvas.create_oval(
                cx - 75, cy - 25, cx + 75, cy + 30,
                fill=COLOR_HOLE_OUTER, outline="#3e2723", width=2
            )
            # 穴の内部（影・深さ）
            self.canvas.create_oval(
                cx - 65, cy - 18, cx + 65, cy + 22,
                fill=COLOR_HOLE_INNER, outline=""
            )

    def _draw_grass(self, x: float, y: float) -> None:
        """草の飾りを描画"""
        self.canvas.create_line(x, y, x - 6, y - 10, fill="#558b2f", width=3, capstyle="round")
        self.canvas.create_line(x, y, x, y - 13, fill="#689f38", width=3, capstyle="round")
        self.canvas.create_line(x, y, x + 6, y - 9, fill="#558b2f", width=3, capstyle="round")

    def show_start_screen(self) -> None:
        """スタート画面（ゲーム開始前）の表示"""
        self.overlay_tag = "start_overlay"
        # 半透明風の暗幕
        self.canvas.create_rectangle(
            60, 130, WINDOW_WIDTH - 60, 550,
            fill="#ffffff", outline="#2e7d32", width=4,
            tags=self.overlay_tag
        )

        # タイトル & 説明
        self.canvas.create_text(
            WINDOW_WIDTH / 2, 200,
            text="★ もぐらたたき ★",
            fill="#2e7d32",
            font=("Meiryo", 26, "bold"),
            tags=self.overlay_tag
        )
        self.canvas.create_text(
            WINDOW_WIDTH / 2, 260,
            text="制限時間は 30 秒！\n出てきたモグラをすばやくクリックして叩こう！",
            fill="#333333",
            font=("Meiryo", 14),
            justify="center",
            tags=self.overlay_tag
        )

        # モグラの見本イラストを中央に描画
        sample_cx = WINDOW_WIDTH / 2
        sample_cy = 360
        self.draw_mole_at(sample_cx, sample_cy, tag=self.overlay_tag, is_hit=False)

        # スタートボタン
        self._create_button(
            WINDOW_WIDTH / 2, 470,
            text="ゲームスタート！",
            command=self.start_game,
            tags=self.overlay_tag
        )

    def _create_button(self, cx: float, cy: float, text: str, command, tags: str) -> None:
        """キャンバス上に可愛い角丸風ボタンを作成"""
        w, h = 180, 50
        x1, y1 = cx - w / 2, cy - h / 2
        x2, y2 = cx + w / 2, cy + h / 2

        btn_bg = self.canvas.create_rectangle(
            x1, y1, x2, y2,
            fill=COLOR_BTN, outline="#e65100", width=3,
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
            self.canvas.itemconfig(btn_bg, fill=COLOR_BTN_HOVER)
        def on_leave(e):
            self.canvas.itemconfig(btn_bg, fill=COLOR_BTN)
        def on_press(e):
            command()

        for item in (btn_bg, btn_txt):
            self.canvas.tag_bind(item, "<Enter>", on_enter)
            self.canvas.tag_bind(item, "<Leave>", on_leave)
            self.canvas.tag_bind(item, "<Button-1>", on_press)

    def start_game(self) -> None:
        """ゲームを開始する"""
        self.canvas.delete("start_overlay")
        self.canvas.delete("gameover_overlay")

        # 状態リセット
        self.is_playing = True
        self.score = 0
        self.time_left = GAME_TIME
        for mole in self.moles:
            self._hide_mole(mole)

        self.update_hud()

        # タイマースタート
        self.tick_timer()
        self.spawn_mole_loop()

    def update_hud(self) -> None:
        """HUD（スコア・残り時間）の更新"""
        self.canvas.itemconfig(self.score_text, text=f"スコア: {self.score}")
        
        # 残り時間が少なくなったら文字を赤くする
        color = "#ff5252" if self.time_left <= 5 else "#ffffff"
        self.canvas.itemconfig(self.time_text, text=f"残り時間: {self.time_left}秒", fill=color)

    def tick_timer(self) -> None:
        """1秒ごとの時間カウントダウン"""
        if not self.is_playing:
            return

        self.update_hud()

        if self.time_left <= 0:
            self.game_over()
            return

        self.time_left -= 1
        self.timer_id = self.root.after(1000, self.tick_timer)

    def spawn_mole_loop(self) -> None:
        """一定間隔でモグラを穴から出現させるループ"""
        if not self.is_playing:
            return

        # 隠れている穴を探す
        hidden_indices = [i for i, m in enumerate(self.moles) if m["state"] == "hidden"]
        if hidden_indices:
            # 穴をランダムに1〜2箇所選択
            num_to_spawn = 1
            if len(hidden_indices) >= 3 and random.random() < 0.35:
                num_to_spawn = 2
            
            chosen_indices = random.sample(hidden_indices, min(num_to_spawn, len(hidden_indices)))
            for idx in chosen_indices:
                self.pop_up_mole(idx)

        # 残り時間に応じて出現間隔を徐々に短く（難易度アップ）
        if self.time_left > 20:
            next_delay = random.randint(700, 1100)
        elif self.time_left > 10:
            next_delay = random.randint(550, 900)
        else:
            next_delay = random.randint(450, 750)

        self.spawn_timer_id = self.root.after(next_delay, self.spawn_mole_loop)

    def pop_up_mole(self, index: int) -> None:
        """指定の穴にモグラを出現させる"""
        mole = self.moles[index]
        mole["state"] = "up"

        cx, cy = self.holes[index]
        # モグラを描画
        self.draw_mole_at(cx, cy, tag=mole["tag"], is_hit=False)

        # 残り時間に応じて出ている時間を調整（800ms〜1300ms）
        stay_time = max(600, int(1100 - (GAME_TIME - self.time_left) * 15))
        mole["hide_id"] = self.root.after(stay_time, lambda: self._on_mole_timeout(index))

    def _on_mole_timeout(self, index: int) -> None:
        """叩かれずに時間切れで引っ込む"""
        mole = self.moles[index]
        if mole["state"] == "up":
            self._hide_mole(mole)

    def _hide_mole(self, mole: dict) -> None:
        """モグラを穴に引っ込める"""
        if mole["hide_id"] is not None:
            self.root.after_cancel(mole["hide_id"])
            mole["hide_id"] = None
        self.canvas.delete(mole["tag"])
        mole["state"] = "hidden"

    def draw_mole_at(self, cx: float, cy: float, tag: str, is_hit: bool = False) -> None:
        """指定位置にモグラを描画する"""
        self.canvas.delete(tag)

        mole_top = cy - 70
        mole_w = 42

        # 1. 耳（左右）
        self.canvas.create_oval(
            cx - 38, mole_top + 10, cx - 18, mole_top + 30,
            fill="#6d4c41", outline="", tags=tag
        )
        self.canvas.create_oval(
            cx + 18, mole_top + 10, cx + 38, mole_top + 30,
            fill="#6d4c41", outline="", tags=tag
        )

        # 2. 体・頭部
        self.canvas.create_oval(
            cx - mole_w, mole_top, cx + mole_w, cy + 10,
            fill=COLOR_MOLE, outline="#4e342e", width=2, tags=tag
        )

        # 3. 口元・お腹（白い楕円）
        self.canvas.create_oval(
            cx - 24, cy - 35, cx + 24, cy - 2,
            fill=COLOR_MOLE_BELLY, outline="", tags=tag
        )

        # 4. 鼻（赤／ピンクの丸）
        self.canvas.create_oval(
            cx - 10, cy - 35, cx + 10, cy - 21,
            fill=COLOR_NOSE, outline="#d32f2f", width=1, tags=tag
        )

        # 5. 目（通常時 or 叩かれた時）
        if is_hit:
            # 叩かれた時の目: 「× ×」
            # 左目
            self.canvas.create_line(cx - 24, mole_top + 23, cx - 12, mole_top + 33, fill="#3e2723", width=3, tags=tag)
            self.canvas.create_line(cx - 12, mole_top + 23, cx - 24, mole_top + 33, fill="#3e2723", width=3, tags=tag)
            # 右目
            self.canvas.create_line(cx + 12, mole_top + 23, cx + 24, mole_top + 33, fill="#3e2723", width=3, tags=tag)
            self.canvas.create_line(cx + 24, mole_top + 23, cx + 12, mole_top + 33, fill="#3e2723", width=3, tags=tag)

            # 口: 波線（いたたた...）
            self.canvas.create_line(cx - 8, cy - 12, cx + 8, cy - 12, fill="#5d4037", width=2, tags=tag)

            # 頭の上の星（ピヨピヨ演出）
            self._draw_star(cx - 25, mole_top - 5, tag)
            self._draw_star(cx + 25, mole_top - 5, tag)
        else:
            # つぶらな黒目
            self.canvas.create_oval(
                cx - 22, mole_top + 22, cx - 12, mole_top + 34,
                fill="#212121", outline="", tags=tag
            )
            self.canvas.create_oval(
                cx + 12, mole_top + 22, cx + 22, mole_top + 34,
                fill="#212121", outline="", tags=tag
            )
            # 目のハイライト（白）
            self.canvas.create_oval(
                cx - 20, mole_top + 24, cx - 15, mole_top + 29,
                fill="#ffffff", outline="", tags=tag
            )
            self.canvas.create_oval(
                cx + 14, mole_top + 24, cx + 19, mole_top + 29,
                fill="#ffffff", outline="", tags=tag
            )

            # ほっぺた（ピンク）
            self.canvas.create_oval(
                cx - 32, mole_top + 32, cx - 20, mole_top + 42,
                fill="#ffab91", outline="", tags=tag
            )
            self.canvas.create_oval(
                cx + 20, mole_top + 32, cx + 32, mole_top + 42,
                fill="#ffab91", outline="", tags=tag
            )

            # 口: にっこり
            self.canvas.create_arc(
                cx - 10, cy - 25, cx + 10, cy - 8,
                start=200, extent=140, style="arc",
                outline="#4e342e", width=2, tags=tag
            )

        # 6. 穴の手前側のフチ（モグラの下半身が穴の中に隠れて見えるように重ね描画）
        self.canvas.create_arc(
            cx - 65, cy - 18, cx + 65, cy + 22,
            start=180, extent=180, fill=COLOR_HOLE_OUTER,
            outline="#3e2723", width=2, tags=tag
        )

    def _draw_star(self, sx: float, sy: float, tag: str) -> None:
        """星マークを描画（ヒット演出）"""
        self.canvas.create_text(
            sx, sy,
            text="★",
            fill=COLOR_STAR,
            font=("Meiryo", 16, "bold"),
            tags=tag
        )

    def on_click(self, event) -> None:
        """キャンバスクリック時の処理"""
        if not self.is_playing:
            return

        mx, my = event.x, event.y

        # 出現中のモグラをクリックしたか判定
        hit_any = False
        for i, mole in enumerate(self.moles):
            if mole["state"] != "up":
                continue

            cx, cy = self.holes[i]
            # モグラの当たり判定範囲（円または矩形近似）
            # モグラの中心はおよそ (cx, cy - 30) 付近
            dx = mx - cx
            dy = my - (cy - 30)
            distance = math.hypot(dx, dy)

            if distance < 50:
                self.hit_mole(i, mx, my)
                hit_any = True
                break

    def hit_mole(self, index: int, hit_x: float, hit_y: float) -> None:
        """モグラを叩いたときの処理"""
        mole = self.moles[index]
        mole["state"] = "hit"

        # タイマーキャンセル
        if mole["hide_id"] is not None:
            self.root.after_cancel(mole["hide_id"])
            mole["hide_id"] = None

        # スコア加算
        self.score += 10
        self.update_hud()

        # 叩かれたモグラを描画
        cx, cy = self.holes[index]
        self.draw_mole_at(cx, cy, tag=mole["tag"], is_hit=True)

        # ポップアップテキスト（「+10 HIT!」）
        self.show_hit_effect(cx, cy - 70)

        # 少しピヨピヨした後に引っ込む（300ms後）
        mole["hide_id"] = self.root.after(300, lambda: self._hide_mole(mole))

    def show_hit_effect(self, x: float, y: float) -> None:
        """叩いた瞬間のエフェクト表示"""
        effect_tag = f"effect_{random.randint(1000, 9999)}"
        txt = self.canvas.create_text(
            x, y,
            text="HIT! +10",
            fill="#ffeb3b",
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
        """ゲーム終了時の処理"""
        self.is_playing = False

        if self.timer_id is not None:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
        if self.spawn_timer_id is not None:
            self.root.after_cancel(self.spawn_timer_id)
            self.spawn_timer_id = None

        for mole in self.moles:
            self._hide_mole(mole)

        self.show_game_over_screen()

    def show_game_over_screen(self) -> None:
        """ゲームオーバー（リザルト）画面の表示"""
        self.overlay_tag = "gameover_overlay"

        # 背景パネル
        self.canvas.create_rectangle(
            60, 140, WINDOW_WIDTH - 60, 540,
            fill="#ffffff", outline="#e65100", width=4,
            tags=self.overlay_tag
        )

        # タイムアップ表示
        self.canvas.create_text(
            WINDOW_WIDTH / 2, 200,
            text="タイムアップ！",
            fill="#d32f2f",
            font=("Meiryo", 24, "bold"),
            tags=self.overlay_tag
        )

        # 最終スコア
        self.canvas.create_text(
            WINDOW_WIDTH / 2, 260,
            text=f"あなたのスコア: {self.score} 点",
            fill="#212121",
            font=("Meiryo", 22, "bold"),
            tags=self.overlay_tag
        )

        # スコアに応じたランク評価メッセージ
        if self.score >= 250:
            rank_text = "称号: 伝説のもぐらマスター！✨\nものすごい速さです！"
            rank_color = "#f57c00"
        elif self.score >= 180:
            rank_text = "称号: もぐらハンター名人！🏆\nすばらしい腕前！"
            rank_color = "#388e3c"
        elif self.score >= 100:
            rank_text = "称号: 一人前のもぐらハンター！👍\nナイスファイト！"
            rank_color = "#1976d2"
        else:
            rank_text = "称号: 見習いハンター！🐣\n次はもっと叩けるかも！"
            rank_color = "#616161"

        self.canvas.create_text(
            WINDOW_WIDTH / 2, 335,
            text=rank_text,
            fill=rank_color,
            font=("Meiryo", 14, "bold"),
            justify="center",
            tags=self.overlay_tag
        )

        # もう一度遊ぶボタン
        self._create_button(
            WINDOW_WIDTH / 2, 450,
            text="もう一度あそぶ",
            command=self.start_game,
            tags=self.overlay_tag
        )


def main() -> None:
    root = tk.Tk()
    MoleGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()

