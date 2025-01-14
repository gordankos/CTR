
from Settings.app_env import WindowTheme
from Core.product import NutritionData

import math
import pyqtgraph as pg
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtGui import QPainter, QFont, QColor, QPen
from PySide6.QtCore import QRectF, Qt


LIGHT_THEME_TEXT_COLOR: QColor = QColor("black")
LIGHT_THEME_BACKGROUND_COLOR: QColor = QColor(248, 249, 250)

DARK_THEME_TEXT_COLOR: QColor = QColor("white")
DARK_THEME_BACKGROUND_COLOR: QColor = QColor(32, 33, 36)

DONUT_CHART_FAT_COLOR = QColor(255, 99, 71)
DONUT_CHART_CARBS_COLOR = QColor(255, 215, 0)
DONUT_CHART_PROTEIN_COLOR = QColor(144, 238, 144)


def get_background_color(theme: WindowTheme):
    if theme is WindowTheme.DARK:
        return DARK_THEME_BACKGROUND_COLOR
    else:
        return LIGHT_THEME_BACKGROUND_COLOR


def get_text_color(theme: WindowTheme):
    if theme is WindowTheme.DARK:
        return DARK_THEME_TEXT_COLOR
    else:
        return LIGHT_THEME_TEXT_COLOR


class DonutChart(pg.GraphicsObject):
    """
    A custom pyqtgraph GraphicsObject that draws a segmented donut chart.
    Each segment represents the calorie contribution from fat, carbs, and protein.
    The total calories are shown in the center, and each segment is labeled (white text)
    with its macronutrient name and amount in grams.
    """

    def __init__(self, nutrition_data: NutritionData,
                 background_color: QColor = QColor("white"),
                 text_color: QColor = QColor("black"),
                 radius: int = 200):
        super().__init__()
        self.nutrition_data = nutrition_data
        self.background_color = background_color
        self.text_color = text_color
        self.radius = radius

        self.inner_radius = self.radius * 0.6

        self.colors = [
            DONUT_CHART_FAT_COLOR,
            DONUT_CHART_CARBS_COLOR,
            DONUT_CHART_PROTEIN_COLOR
        ]
        self.labels: list[str] = []

        self.update_labels()

        # self.total_text_item = pg.TextItem("", anchor=(0.5, 0.5), color="black")
        # # self.total_text_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations, True)
        # self.total_text_item.setParentItem(self)
        #
        # self.fat_text_item = pg.TextItem("Fat", anchor=(0.5, 0.5), color="white")
        # # self.fat_text_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations, True)
        # self.fat_text_item.setParentItem(self)
        #
        # self.carbs_text_item = pg.TextItem("Carbs", anchor=(0.5, 0.5), color="white")
        # # self.carbs_text_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations, True)
        # self.carbs_text_item.setParentItem(self)
        #
        # self.protein_text_item = pg.TextItem("Protein", anchor=(0.5, 0.5), color="white")
        # # self.protein_text_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations, True)
        # self.protein_text_item.setParentItem(self)
        #
        # total_font = QFont("Arial", 16, QFont.Bold)
        # self.total_text_item.setFont(total_font)
        # seg_font = QFont("Arial", 10, QFont.Bold)
        # self.fat_text_item.setFont(seg_font)
        # self.carbs_text_item.setFont(seg_font)
        # self.protein_text_item.setFont(seg_font)

    def update_labels(self):
        self.labels = [
            f"Fat\n{self.nutrition_data.fat:.0f} g",
            f"Carbs\n{self.nutrition_data.carbs:.0f} g",
            f"Protein\n{self.nutrition_data.protein:.0f} g",
        ]

    def paint(self, painter, option, widget) -> None:           # noqa
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        segment_info = self.draw_pie_chart(painter)
        self.draw_inner_circle(painter)
        self.draw_segment_labels(painter, segment_info)
        self.draw_total_calories(painter)

    # def paint(self, painter, option, widget):
    #     # Enable antialiasing for smooth drawing.
    #     painter.setRenderHint(QPainter.Antialiasing)
    #
    #     # --- Calculate calorie contributions for each macronutrient ---
    #     fat_cal = self.nutrition_data.fat * 9
    #     carbs_cal = self.nutrition_data.carbs * 4
    #     protein_cal = self.nutrition_data.protein * 4
    #     total_macro_cal = fat_cal + carbs_cal + protein_cal
    #
    #     if total_macro_cal > 0:
    #         perc_fat = fat_cal / total_macro_cal
    #         perc_carbs = carbs_cal / total_macro_cal
    #         perc_protein = protein_cal / total_macro_cal
    #     else:
    #         perc_fat = perc_carbs = perc_protein = 0
    #
    #     # --- Define colors for segments ---
    #     colors = [QColor("#FF6347"),  # Tomato for Fat
    #               QColor("#FFD700"),  # Gold for Carbs
    #               QColor("#90EE90")]  # Light Green for Protein
    #
    #     # --- Draw the outer donut segments ---
    #     rect = QRectF(-self.radius, -self.radius, 2 * self.radius, 2 * self.radius)
    #     painter.save()
    #     start_angle = 0.0
    #     segment_angles = []  # store mid-angles for each segment for positioning labels
    #     for perc, color in zip([perc_fat, perc_carbs, perc_protein], colors):
    #         span_angle = perc * 360.0
    #         painter.setPen(Qt.NoPen)
    #         painter.setBrush(color)
    #         # QPainter.drawPie expects angles in 1/16th of a degree.
    #         painter.drawPie(rect, int(start_angle * 16), int(span_angle * 16))
    #         if span_angle > 0:
    #             mid_angle = start_angle + span_angle / 2.0
    #             segment_angles.append(mid_angle)
    #         start_angle += span_angle
    #     painter.restore()
    #
    #     # --- Draw inner white circle to create the donut effect ---
    #     self.inner_radius = self.radius * 0.6
    #     inner_rect = QRectF(-self.inner_radius, -self.inner_radius, 2 * self.inner_radius, 2 * self.inner_radius)
    #     painter.save()
    #     painter.setPen(Qt.NoPen)
    #     painter.setBrush(QColor("white"))
    #     painter.drawEllipse(inner_rect)
    #     painter.restore()
    #
    #     # --- Update positions of the text items (they ignore transformations) ---
    #     # Total calories text centered at (0,0)
    #     self.total_text_item.setText(f"{self.nutrition_data.calories:.0f} Cal")
    #     self.total_text_item.setPos(0, 0)
    #
    #     # For the segment labels, place them halfway in the donut ring.
    #     # Use the average radius between outer and inner edges.
    #     label_radius = (self.radius + self.inner_radius) / 2.0
    #     if len(segment_angles) >= 3:
    #         # Fat label (first segment)
    #         rad = math.radians(segment_angles[0])
    #         self.fat_text_item.setPos(label_radius * math.cos(rad), label_radius * math.sin(rad))
    #         # Carbs label (second segment)
    #         rad = math.radians(segment_angles[1])
    #         self.carbs_text_item.setPos(label_radius * math.cos(rad), label_radius * math.sin(rad))
    #         # Protein label (third segment)
    #         rad = math.radians(segment_angles[2])
    #         self.protein_text_item.setPos(label_radius * math.cos(rad), label_radius * math.sin(rad))

    def draw_pie_chart(self, painter: QPainter):
        """
        Draws the pie chart. Note: QPainter.drawPie expects angles in 1/16th of a degree.
        """
        macro_calories = self.nutrition_data.get_macro_calories()
        fat_cal, carbs_cal, protein_cal = macro_calories
        total_macro_cal = sum(macro_calories)

        if total_macro_cal > 0:
            perc_fat = fat_cal / total_macro_cal
            perc_carbs = carbs_cal / total_macro_cal
            perc_protein = protein_cal / total_macro_cal
        else:
            perc_fat = perc_carbs = perc_protein = 0

        rect = QRectF(-self.radius, -self.radius, 2 * self.radius, 2 * self.radius)
        painter.save()
        start_angle = 0.0
        segment_info = []

        for perc, color, label in zip([perc_fat, perc_carbs, perc_protein], self.colors, self.labels):
            span_angle = perc * 360.0
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(color)
            painter.drawPie(rect, int(start_angle * 16), int(span_angle * 16))

            if span_angle > 0:
                mid_angle = start_angle + span_angle / 2.0
                segment_info.append((mid_angle, label))
            start_angle += span_angle
        painter.restore()

        return segment_info

    def draw_segment_labels(self, painter: QPainter, segment_info: list,
                            text_color: QColor = QColor("black")):
        """
        Draw segment labels inside the donut segments
        """
        painter.save()
        if painter.transform().m22() < 0:   # Fix for text mirroring
            painter.scale(1, -1)
        label_font = QFont("Arial", 8, QFont.Weight.Bold)
        painter.setFont(label_font)
        painter.setPen(text_color)

        label_radius = (self.radius + self.inner_radius) / 2.0
        for mid_angle, label in segment_info:
            rad = math.radians(mid_angle)
            x = label_radius * math.cos(rad)
            y = label_radius * math.sin(rad)
            fm = painter.fontMetrics()
            text_width = fm.horizontalAdvance(label)
            text_height = fm.height() * 2
            text_rect = QRectF(x - text_width / 2, y - text_height / 2, text_width, text_height)
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, label)
        painter.restore()

    def draw_inner_circle(self, painter: QPainter):
        """
        Draws inner circle with the same background color to create the donut effect
        """
        inner_rect = QRectF(-self.inner_radius, -self.inner_radius, 2 * self.inner_radius, 2 * self.inner_radius)
        painter.save()
        painter.setBrush(self.background_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(inner_rect)
        painter.restore()

    def draw_total_calories(self, painter: QPainter):
        """
        Draws total calories in the center of the donut chart.
        """
        painter.save()
        if painter.transform().m22() < 0:   # Fix for text mirroring
            painter.scale(1, -1)
        painter.setPen(self.text_color)
        total_font = QFont("Arial", 16, QFont.Weight.Bold)
        painter.setFont(total_font)
        total_text = f"{self.nutrition_data.calories:.0f}\nkcal"
        fm_total = painter.fontMetrics()
        total_text_width = fm_total.horizontalAdvance(total_text)
        total_text_height = fm_total.height() * 2
        total_text_rect = QRectF(-total_text_width / 2, -total_text_height / 2, total_text_width, total_text_height)
        painter.drawText(total_text_rect, Qt.AlignmentFlag.AlignCenter, total_text)
        painter.restore()

    def boundingRect(self):
        return QRectF(-self.radius, -self.radius, 2 * self.radius, 2 * self.radius)


class DailyIntakeWidget(QWidget):
    def __init__(self, parent=None):
        """
        Custom widget that displays a segmented donut chart with total calories in the center,
        and macronutrient labels (Fat, Carbs, Protein) drawn inside each segment.
        """
        super().__init__(parent)

        self.nutrition_data = NutritionData()

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        self.plot_widget = pg.PlotWidget()

        self.plot_widget.setBackground('w')
        self.plot_widget.setMouseEnabled(x=False, y=False)
        self.plot_widget.hideAxis('left')
        self.plot_widget.hideAxis('bottom')
        self.plot_widget.getViewBox().setAspectLocked(True)

        layout.addWidget(self.plot_widget)

        self.donut_chart = DonutChart(self.nutrition_data, radius=100)
        self.plot_widget.addItem(self.donut_chart)

    def update_theme_colors(self, theme: WindowTheme):
        background_color = get_background_color(theme=theme)
        text_color = get_text_color(theme=theme)

        self.plot_widget.setBackground(background_color)
        self.donut_chart.background_color = background_color
        self.donut_chart.text_color = text_color

    def update_data(self, data: NutritionData):
        self.nutrition_data = data
        self.donut_chart.nutrition_data = data
        self.donut_chart.update_labels()
        self.donut_chart.update()


class DonutChartTargetWidget(QWidget):
    def __init__(
            self,
            parent=None,
            size: int = 80,
            current_value: float = 2000.0,
            target_value: float = 2500.0,
            unit_label: str = "",
            background_color: QColor = QColor("white"),
            text_color: QColor = QColor("black"),
            show_percentage: bool = True
    ):
        """
        Custom widget that displays a progress donut chart with the current value in the center.
        """
        super().__init__(parent)
        self.size = size
        self.current_value = current_value
        self.target_value = target_value
        self.unit_label = unit_label
        self.background_color = background_color
        self.text_color = text_color
        self.show_percentage = show_percentage

        if show_percentage:
            self.unit_label = "%"

        self.setMinimumSize(self.size, self.size)
        self.setMaximumSize(self.size, self.size)

        self.thickness = self.size * 0.1

    def update_theme_colors(self, theme: WindowTheme):
        background_color = get_background_color(theme=theme)
        text_color = get_text_color(theme=theme)

        self.background_color = background_color
        self.text_color = text_color

    def set_values(self, current: float, target: float):
        """
        Update the current and target calorie values.
        """
        self.current_value = current
        self.target_value = target
        self.update()

    def get_percentage(self) -> float:
        return (self.current_value / self.target_value) * 100 if self.target_value > 0 else 0.0

    @staticmethod
    def interpolate_color(color1: QColor, color2: QColor, fraction: float) -> QColor:
        """
        Linearly interpolates between two colors.
        Fraction should be in the range [0, 1].
        """
        r = color1.red() + fraction * (color2.red() - color1.red())
        g = color1.green() + fraction * (color2.green() - color1.green())
        b = color1.blue() + fraction * (color2.blue() - color1.blue())
        return QColor(int(r), int(g), int(b))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Determine a square drawing area based on the widget size.
        w, h = self.width(), self.height()
        size = min(w, h)
        margin = size * 0.1  # Margin for aesthetics
        rect = QRectF(margin, margin, size - 2 * margin, size - 2 * margin)

        # Draw the background circle (target) in light gray.
        background_color = QColor(220, 220, 220)
        pen = QPen(background_color, self.thickness, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawArc(rect, 0, 360 * 16)

        # Compute the progress ratio.
        ratio = self.current_value / self.target_value if self.target_value > 0 else 0.0
        draw_ratio = min(ratio, 1.0)  # The drawn arc only goes up to 100%
        angle = int(draw_ratio * 360 * 16)  # QPainter uses angles in 1/16th degree

        # Determine the arc color.
        if ratio <= 1.0:
            # Interpolate from red (0% of target) to green (100% of target).
            color = self.interpolate_color(QColor("red"), QColor("green"), ratio)
        else:
            # When over target, shift from green back toward red.
            extra_fraction = min((ratio - 1.0) / 0.5, 1.0)
            color = self.interpolate_color(QColor("green"), QColor("red"), extra_fraction)

        pen = QPen(color, self.thickness, Qt.PenStyle.SolidLine, Qt.PenCapStyle.FlatCap)
        painter.setPen(pen)
        # Start at 12 o’clock (90°) and draw clockwise (hence negative span angle).
        startAngle = 90 * 16
        painter.drawArc(rect, startAngle, -angle)

        # --- Draw the center text: numeric calorie value with "kcal" below ---
        painter.setPen(self.text_color)
        center = rect.center()

        # Define the texts.
        if self.show_percentage:
            numeric_text = f"{self.get_percentage():.0f}"
        else:
            numeric_text = f"{self.current_value:.0f}"

        # Set up fonts:
        numeric_font = QFont("Arial", 16, QFont.Weight.Bold)
        unit_font = QFont("Arial", 8)

        # Get font metrics for each.
        painter.setFont(numeric_font)
        numeric_metrics = painter.fontMetrics()
        numeric_text_width = numeric_metrics.horizontalAdvance(numeric_text)
        numeric_text_height = numeric_metrics.height()

        painter.setFont(unit_font)
        unit_metrics = painter.fontMetrics()
        unit_text_width = unit_metrics.horizontalAdvance(self.unit_label)
        unit_text_height = unit_metrics.height()

        # The combined height of the two lines.
        combined_height = numeric_text_height + unit_text_height

        # Build bounding rectangles for the numeric text and the unit text.
        numeric_rect = QRectF(0, 0, numeric_text_width, numeric_text_height)
        unit_rect = QRectF(0, 0, unit_text_width, unit_text_height)

        # Center both rects horizontally on the widget.
        numeric_rect.moveCenter(center)
        unit_rect.moveCenter(center)

        # Adjust vertically so that the numeric text is above and the unit text is below,
        # with the combined block centered.
        numeric_rect.moveTop(center.y() - combined_height / 2)
        unit_rect.moveTop(center.y() - combined_height / 2 + numeric_text_height)

        # Draw the numeric calorie value.
        painter.setFont(numeric_font)
        painter.drawText(numeric_rect, Qt.AlignmentFlag.AlignCenter, numeric_text)

        # Draw the unit label below.
        painter.setFont(unit_font)
        painter.drawText(unit_rect, Qt.AlignmentFlag.AlignCenter, self.unit_label)
