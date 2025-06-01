import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel, QComboBox, QCheckBox, QTextEdit, 
                            QGraphicsView, QGraphicsScene, QGraphicsPixmapItem)
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor, QBrush
import requests
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
import io
import svgwrite

class TulipDiagram:
    def __init__(self):
        self.direction = "straight"
        self.icons = []
    
    def to_svg(self):
        dwg = svgwrite.Drawing(size=("50mm", "20mm"))
        
        if self.direction == "left":
            dwg.add(dwg.polyline([(10, 10), (0, 20), (10, 30)]))
        elif self.direction == "right":
            dwg.add(dwg.polyline([(40, 10), (50, 20), (40, 30)]))
        else:  # straight
            dwg.add(dwg.line((10, 20), (40, 20)))
        
        for icon in self.icons:
            if icon == "house":
                dwg.add(dwg.rect((25, 10), (15, 10)))
            elif icon == "river":
                dwg.add(dwg.path(d="M 15,25 C 20,20 30,20 35,25"))
        
        return dwg.tostring()

class MapWidget(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        
        # Load a simple map background (in a real app, you'd use proper map tiles)
        self.map_background = QPixmap(800, 600)
        self.map_background.fill(Qt.white)
        
        # Draw some simple roads for demonstration
        painter = QPainter(self.map_background)
        painter.setPen(QPen(Qt.black, 3))
        painter.drawLine(100, 100, 700, 100)  # horizontal road
        painter.drawLine(400, 100, 400, 500)  # vertical road
        painter.drawLine(100, 500, 700, 500)  # another horizontal road
        painter.end()
        
        self.background = self.scene.addPixmap(self.map_background)
        self.route_points = []
        self.route_lines = []
        self.markers = []
        
        self.setDragMode(QGraphicsView.ScrollHandDrag)
    
    def add_route_point(self, pos):
        # Convert view coordinates to scene coordinates
        scene_pos = self.mapToScene(pos)
        
        # Add marker
        marker = self.scene.addEllipse(scene_pos.x()-5, scene_pos.y()-5, 10, 10, 
                                     QPen(Qt.red), QBrush(Qt.red))
        self.markers.append(marker)
        self.route_points.append((scene_pos.x(), scene_pos.y()))
        
        # Draw lines between points
        if len(self.route_points) > 1:
            prev_point = self.route_points[-2]
            line = self.scene.addLine(prev_point[0], prev_point[1], 
                                    scene_pos.x(), scene_pos.y(), 
                                    QPen(Qt.blue, 2))
            self.route_lines.append(line)
        
        return len(self.route_points) - 1  # Return point index
    
    def clear_route(self):
        for marker in self.markers:
            self.scene.removeItem(marker)
        for line in self.route_lines:
            self.scene.removeItem(line)
        self.route_points = []
        self.route_lines = []
        self.markers = []

class RoadbookGenerator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Rally Roadbook Generator")
        self.setGeometry(100, 100, 1200, 800)
        
        # Main widget and layout
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.layout = QHBoxLayout(self.main_widget)
        
        # Left side - Map and controls
        self.left_panel = QWidget()
        self.left_layout = QVBoxLayout(self.left_panel)
        
        # Map widget
        self.map_widget = MapWidget()
        self.left_layout.addWidget(self.map_widget)
        
        # Controls
        self.controls_layout = QHBoxLayout()
        
        self.profile_combo = QComboBox()
        self.profile_combo.addItems(["Motorcycle", "Bicycle (Road)", "Bicycle (Mountain)", "Walking"])
        
        self.add_point_btn = QPushButton("Add Route Point")
        self.add_point_btn.clicked.connect(self.toggle_add_point_mode)
        
        self.clear_btn = QPushButton("Clear Route")
        self.clear_btn.clicked.connect(self.clear_route)
        
        self.update_btn = QPushButton("Update Preview")
        self.update_btn.clicked.connect(self.update_preview)
        
        self.export_btn = QPushButton("Export PDF")
        self.export_btn.clicked.connect(self.export_pdf)
        
        self.controls_layout.addWidget(self.profile_combo)
        self.controls_layout.addWidget(self.add_point_btn)
        self.controls_layout.addWidget(self.clear_btn)
        self.controls_layout.addWidget(self.update_btn)
        self.controls_layout.addWidget(self.export_btn)
        
        self.left_layout.addLayout(self.controls_layout)
        
        # Right side - Preview
        self.right_panel = QWidget()
        self.right_layout = QVBoxLayout(self.right_panel)
        
        self.unit_check = QCheckBox("Use Kilometers")
        self.unit_check.setChecked(True)
        self.right_layout.addWidget(self.unit_check)
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.right_layout.addWidget(self.preview_text)
        
        # Add both panels to main layout
        self.layout.addWidget(self.left_panel, 2)
        self.layout.addWidget(self.right_panel, 1)
        
        # Route data
        self.tulips = []
        self.notes = []
        self.add_point_mode = False
        self.original_cursor = self.map_widget.cursor()
    
    def toggle_add_point_mode(self):
        self.add_point_mode = not self.add_point_mode
        if self.add_point_mode:
            self.add_point_btn.setStyleSheet("background-color: #0d6efd; color: white")
            self.map_widget.setCursor(Qt.CrossCursor)
            self.map_widget.setDragMode(QGraphicsView.NoDrag)
        else:
            self.add_point_btn.setStyleSheet("")
            self.map_widget.setCursor(self.original_cursor)
            self.map_widget.setDragMode(QGraphicsView.ScrollHandDrag)
    
    def mousePressEvent(self, event):
        if self.add_point_mode and event.button() == Qt.LeftButton:
            pos = self.map_widget.mapFromGlobal(event.globalPos())
            point_index = self.map_widget.add_route_point(pos)
            
            # Add empty tulip and note for this point
            if point_index >= len(self.tulips):
                self.tulips.append(TulipDiagram())
                self.notes.append("")
            
            # Update preview
            self.update_preview()
        
        super().mousePressEvent(event)
    
    def clear_route(self):
        self.map_widget.clear_route()
        self.tulips = []
        self.notes = []
        self.preview_text.clear()
    
    def update_preview(self):
        if len(self.map_widget.route_points) < 2:
            self.preview_text.setPlainText("Add at least 2 points to generate a route")
            return
        
        # In a real app, you would call the OpenRouteService API here
        # For this example, we'll just show the points
        
        preview_text = "ROADBOOK PREVIEW\n\n"
        unit = "km" if self.unit_check.isChecked() else "m"
        
        for i in range(len(self.map_widget.route_points)):
            # Calculate distance (simplified for this example)
            distance = (i + 1) * 0.5  # dummy distance
            
            if unit == "km":
                distance_text = f"{distance:.1f}km"
            else:
                distance_text = f"{int(distance * 1000)}m"
            
            tulip_text = f"Tulip: {self.tulips[i].direction}" if i < len(self.tulips) else "Tulip: -"
            note_text = self.notes[i] if i < len(self.notes) else ""
            
            preview_text += f"{distance_text}\t{tulip_text}\t{note_text}\n\n"
        
        self.preview_text.setPlainText(preview_text)
    
    def export_pdf(self):
        if len(self.map_widget.route_points) < 2:
            return
        
        # Create PDF
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        # Set up layout
        left_margin = 10 * mm
        col1_width = 30 * mm
        col2_width = 50 * mm
        col3_width = width - left_margin - col1_width - col2_width
        
        # Header
        c.setFont("Helvetica-Bold", 14)
        c.drawString(left_margin, height - 20 * mm, "Rally Roadbook")
        
        # Content
        y_position = height - 30 * mm
        unit = "km" if self.unit_check.isChecked() else "m"
        
        for i in range(len(self.map_widget.route_points)):
            # Calculate distance (simplified for this example)
            distance = (i + 1) * 0.5  # dummy distance
            if unit == "m":
                distance *= 1000
            
            # Column 1: Distance
            c.setFont("Helvetica", 10)
            c.drawString(left_margin, y_position, f"{distance:.1f}{unit}")
            
            # Column 2: Tulip diagram
            if i < len(self.tulips):
                c.drawString(left_margin + col1_width, y_position, f"[Tulip: {self.tulips[i].direction}]")
            
            # Column 3: Notes
            if i < len(self.notes):
                c.drawString(left_margin + col1_width + col2_width, y_position, self.notes[i])
            
            y_position -= 5 * mm
            if y_position < 20 * mm:
                c.showPage()
                y_position = height - 20 * mm
        
        c.save()
        buffer.seek(0)
        
        # Save to file
        with open("roadbook.pdf", "wb") as f:
            f.write(buffer.getvalue())
        
        self.preview_text.append("\nPDF exported successfully!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RoadbookGenerator()
    window.show()
    sys.exit(app.exec_())
