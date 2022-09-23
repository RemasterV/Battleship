from random import randint



# Объявляем родительский класс "игрок"
class Player:
    # В конструкторе добавляем доски игрока, врага
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy
    # Объявляем метод с генерацией исключения
    # для наследования в дочерних классах
        def ask(self):
            raise NotImplementedError()
    # В бесконечном цикле запрашиваем координаты и делаем по ним выстрел,
    # обрабатываем исключения
    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)

# Объявляем дочерний класс ИИ
class AI(Player):
    # метод по запросу генерирует случайную точку и возвращает её
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}")
        return d

# Объявляем дочерний класс пользователь
class User(Player):
    def ask(self):
        # В бесконечном цикле запрашиваем данные у пользователя,
        # проверяем их правильность. Возвращаем точку с координатами
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print(" Введите 2 координаты! ")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)

class Ship:
    # В инициализаторе добавляем параметры корабля в экземпляр
    def __init__(self, bow, l, o):
        self.bow = bow
        self.l = l
        self.o = o
        self.lives = l
    # Объявляем метод dots, формирующий "тело" корабля
    @property
    def dots(self):
        # список точек "тела" корабля
        ship_dots = []
        # в цикле создаём точки и смещаем их на "i"
        # по гор./верт. в зависимости от ориентации корабля
        for i in range(self.l):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.o == 0:
                cur_x += i

            elif self.o == 1:
                cur_y += i
            # добавляем точки в список на каждой итерации
            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots
    # Метод проверки попадания в корабль(находится ли
    # "точка" выстрела в теле экземпляра корабля)
    def shooten(self, shot):
        return shot in self.dots

# Объявляем родительский класс для обработки исключений
class BoardException(Exception):
    pass
# Объявляем исключение выстрела за доску
class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за доску!"
# Объявляем исключение повторного выстрела
class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"
# Объявляем исключение для расстановки кораблей
class BoardWrongShipException(BoardException):
    pass

# Объявляем класс точка
class Dot:
    # В инициализаторе добавляем координаты в экземпляр
    def __init__(self, x, y):
        self.x = x
        self.y = y

    # Переназначаем метод сравнения экземпляров
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    # Переназначаем отображение экземпляра
    def __repr__(self):
        return f"Dot({self.x}, {self.y})"

# Объявляем класс игровое поле.
class Board:
    # В конструкторе пишем атрибуты экземпляра поля
    def __init__(self, hid=False, size=6):
        self.size = size
        self.hid = hid

        self.count = 0
    # Генератором создаём игровое поле с "0"
        self.field = [["O"] * size for _ in range(size)]

        self.busy = []
        self.ships = []
# Объявляем метод отображения поля в консоли
    def __str__(self):
        res = ""
        # Конструируем игровое поле, пробегая по двумерному списку
        # объединяя элементы вложенного списка методом join,
        # а строки конкатенацией
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"
        # Заменяем видимые корабли на "0", если  hid == True
        if self.hid:
            res = res.replace("■", "O")
        return res
    # Объявляем метод проверки нахождения точки в пределах доски
    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    # Объявляем метод, обводящий контур корабля
    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        # Пробегаем циклом по "телу" корабля, а вложенным
        # циклом по точкам со смещением
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                # Если точка в пределах поля и не занята, добавляем ее
                # в список занятых. Ставим "." если verb==True
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)
    #Объявляем метод, добавляющий корабль
    def add_ship(self, ship):
    # Проверка каждой точки корабля на то, что она не выходит за
    # границы поля и не занята(генерация исключения если это не так)
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        # Все точки корабля помечаем "■" и добавляем в занятые
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)
        # Добавляем список кораблей, обводим по контуру
        self.ships.append(ship)
        self.contour(ship)
    # Объявлям метод "выстрел". Если точка выходит за границы
    # поля или занята, генерируем исключение. Добавляем точку
    # в список занятых
    def shot(self, d):
        if self.out(d):
            raise BoardOutException()

        if d in self.busy:
            raise BoardUsedException()

        self.busy.append(d)
    # Если корабль "подстрелен" точкой, уменьшаем кол-о жизней,
    # помещаем "X" в игровое поле по координатам точки.
        for ship in self.ships:
            if ship.shooten(d):
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                # Если жизни корабля закончились, добавляем 1 к счётчику подбитых кораблей,
                # обводим корабль по контуру, выдаём сообщение "уничтожен",возвращаем False.
                # В противном случае "ранен", True.
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True
        # Корабль не поражён, ставим точку, сообщение мимо, возвращаем False.
        self.field[d.x][d.y] = "."
        print("Мимо!")
        return False
    # обновляем список занятых точек
    def begin(self):
        self.busy = []

# Объявляем класс "игра"
class Game:
    # Конструктор создаёт 2 доски размером size
    def __init__(self, size=6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = False

        self.ai = AI(co, pl)
        self.us = User(pl, co)

# Начальное приветствие
    def greet(self):
        print("-------------------")
        print("  Приветсвуем вас  ")
        print("      в игре       ")
        print("    морской бой    ")
        print("-------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")

    # Метод создания доски
    def try_board(self):
        # Cписок с длинами кораблей
        lens = [3, 2, 2, 1, 1, 1, 1]
        # Генерация доски
        board = Board(size=self.size)
        attempts = 0
        # В цикле пытаемся расставить все корабли, если за 2000
        # попыток не удалось,возвращаем None
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board
    # Бесконечно пытаемся создать доску, пока она None
    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board
    # Основной цикл игры
    def loop(self):
        num = 0
        while True:
            print("-" * 20)
            print("Доска пользователя:")
            print(self.us.board)
            print("-" * 20)
            print("Доска компьютера:")
            print(self.ai.board)
            print("-" * 20)
            if num % 2 == 0:
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.count == 7:
                print("-" * 20)
                print("Пользователь выиграл!")
                break

            if self.us.board.count == 7:
                print("-" * 20)
                print("Компьютер выиграл!")
                break
            num += 1
    # Запуск основной игры
    def start(self):
        self.greet()
        self.loop()

# Создаём экземпляр класса "Игра"
# Выполняем запуск игры
g = Game()
g.start()