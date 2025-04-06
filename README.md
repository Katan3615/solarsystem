# Solar System Simulation

## 🌌 Description (English)

This project is an interactive simulation of a simplified Solar System using Python and Tkinter. It includes planets orbiting the sun, satellites (data nodes) that move in their own orbits, and dynamic data packets that travel between satellites via the shortest available paths (computed using graph algorithms). The simulation also includes collision-aware pathfinding and visualization of a dynamic communication network.

### Key Features
- Real-time animation of celestial objects.
- Orbiting planets and satellites.
- Data generation from satellites and its transfer across the network.
- Dynamic computation and drawing of the **Minimum Spanning Tree (MST)** between satellites, avoiding planet/sun collisions.

### Algorithms Used
- **Circular motion update**: each celestial body moves along its orbit based on angular velocity.
- **Minimum Spanning Tree (MST)** using **Kruskal's algorithm** with **Union-Find (Disjoint Set Union)**.
- **Collision detection** between line segments and circular obstacles.
- **Data packet routing** over the MST network, ensuring each satellite is visited only once per packet.

### Requirements
- Python 3.8+
- Tkinter (usually included by default with Python)

To run:
```bash
python main.py
```

### Future Plans
- Add pause/play buttons and interactive controls (e.g. to add/remove satellites).
- Improve visualization with smoother animations and trails.
- Add labels and tooltips for celestial bodies.
- Export simulation frames to images or video.
- Implement alternative pathfinding (e.g. Dijkstra) and compare efficiency.
- Enable real-time simulation control (e.g. data flow rate, orbital speed).
- Build a web-based version using Pyodide or WebAssembly.
- Modular engine to support other simulations (e.g. planetary traffic, network latency).

---

## 🌌 Описание (Russian)

Этот проект — это интерактивная симуляция Солнечной системы на Python с графикой на Tkinter. В ней планеты вращаются вокруг солнца, а спутники (узлы данных) генерируют данные, которые передаются через сеть по кратчайшим доступным путям.

### Основные возможности
- Анимация объектов в реальном времени.
- Орбиты планет и спутников.
- Генерация и маршрутизация данных по сети.
- Вычисление **минимального остовного дерева (MST)** для спутников, с учётом препятствий в виде планет и солнца.

### Используемые алгоритмы
- Обновление позиции по орбите по угловой скорости.
- Алгоритм Крускала для MST с использованием Union-Find (Disjoint Set).
- Обнаружение пересечений между отрезками и кругами (планеты).
- Передача данных по MST с запоминанием посещённых узлов.

### Необходимое ПО
- Python 3.8+
- Tkinter (обычно уже включён в стандартную библиотеку)

Для запуска:
```bash
python main.py
```

### Планы по развитию
- Добавить кнопки паузы и запуска, а также возможность управлять симуляцией (добавлять/удалять спутники).
- Улучшить визуализацию: добавить шлейфы, более плавную анимацию.
- Подписи объектов, всплывающие подсказки при наведении.
- Экспорт симуляции в изображение или видео.
- Реализация альтернативных алгоритмов маршрутизации (например, Дейкстры).
- Возможность управлять скоростью передачи данных и движением в реальном времени.
- Веб-версия (через Pyodide или WebAssembly).
- Модульность ядра — возможность подключать другие сценарии (например, моделирование трафика, сетевые задержки).

