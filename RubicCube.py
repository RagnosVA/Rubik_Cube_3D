from ursina import *
from rubik_solver import utils

class Game(Ursina):
    def __init__(self, solution1):
        super().__init__()
        window.title = "Rubic's Cube"
        window.borderless, window.exit_button.visible, window.fps_counter.enabled = False, False, False
        camera.rotation = Vec3(30, -45, 0)
        camera.position = Vec3(12.5, 10, -12.5)
        self.model, self.texture = 'models/custom_cube', 'textures/RubikCube'
        self.moves_dict = { 'R':('RIGHT', 90),   "R'":('RIGHT', -90), 'R2':('RIGHT', 180),   "R2'":('RIGHT', -180),
                            'L':('LEFT', -90),   "L'":('LEFT', 90),   'L2':('LEFT', -180),   "L2'":('LEFT', 180),
                            'U':('TOP', 90),     "U'":('TOP', -90),   'U2':('TOP', 180),     "U2'":('TOP', -180),
                            'D':('BOTTOM', -90), "D'":('BOTTOM', 90), 'D2':('BOTTOM', -180), "D2'":('BOTTOM', 180),
                            'F':('FACE', 90),    "F'":('FACE', -90),  'F2':('FACE', 180),    "F2'":('FACE', -180),
                            'B':('BACK', -90),   "B'":('BACK', 90),   'B2':('BACK', -180),   "B2'":('BACK', 180)}
        self.solution = solution1
        self.reverse_sol = self.solution.copy()
        self.num_moves = Text(text = "Moves : " + str(len(self.solution)), x = -0.85, y = 0.4, visible = False)
        self.move_text = [Text(text = move, scale = 1, x = -0.85, y = 0.45, visible = False) for move in self.solution]
        for i in range(1, len(self.move_text)): self.move_text[i].x = self.move_text[i-1].x + 0.078
        for i in range(len(self.reverse_sol)):
            if "'" in self.reverse_sol[i]:
                self.reverse_sol[i] = self.reverse_sol[i][:-1] 
            else:
                self.reverse_sol[i] += "'"
        self.reverse_sol.reverse()
        self.index1, self.index2 = 0, 0
        self.next_button = Button(parent = camera.ui, model = self.model, texture = 'textures/button-next', scale = 0.15, disabled = False, color = color.white, position = Vec2(0.7,0), visible = False)
        self.next_button.on_click = lambda: self.input(key = 'n')
        self.back_button = Button(parent = camera.ui, model = self.model, texture = 'textures/button-back', scale = 0.15, disabled = False, color = color.white, position = Vec2(-0.7,0), visible = False)
        self.back_button.on_click = lambda: self.input(key = 'b')
        self.load_game()
        
    def load_game(self):
        self.cube_positions()
        self.PARENT = Entity()                        
        self.CAMERA_PARENT = Entity()
        camera.parent = self.CAMERA_PARENT
        self.CUBES = [Entity(model = self.model, texture = self.texture, position = pos) for pos in self.SIDE_POSITIONS]
        for cube in self.CUBES : cube.visible = False
        self.rotation_axes = { 'LEFT':'x', 'RIGHT':'x', 'TOP':'y', 'BOTTOM':'y', 'FACE':'z', 'BACK':'z' }
        self.cubes_side_positons = { 'LEFT': self.LEFT, 'BOTTOM': self.BOTTOM, 'RIGHT': self.RIGHT, 'FACE': self.FACE, 'BACK': self.BACK, 'TOP': self.TOP }
        self.action_trigger = True
        self.solve_cube = False
        self.scramble_cube = False
        self.solve_cube_auto = False
        invoke(self.toggle_scramble_cube, delay = 1)

    def cube_positions(self):
        self.FACE   = { Vec3(x, y, -1) for x in range(-1, 2) for y in range(-1, 2) }
        self.BACK   = { Vec3(x, y, 1) for x in range(-1, 2) for y in range(-1, 2) }
        self.LEFT   = { Vec3(-1, y, z) for y in range(-1, 2) for z in range(-1, 2) }
        self.RIGHT  = { Vec3(1, y, z) for y in range(-1, 2) for z in range(-1, 2) }
        self.TOP    = { Vec3(x, 1, z) for x in range(-1, 2) for z in range(-1, 2) }
        self.BOTTOM = { Vec3(x, -1, z) for x in range(-1, 2) for z in range(-1, 2) }
        self.SIDE_POSITIONS = self.FACE | self.BACK | self.LEFT | self.RIGHT | self.TOP | self.BOTTOM

    def toggle_animation_trigger(self):
        self.action_trigger = not self.action_trigger

    def toggle_scramble_cube(self):
        self.loading_text = Text(text = "Finding Solution", scale = 2, y = 0, x = -0.2)
        self.scramble_cube = not self.scramble_cube
        self.update()

    def rotate_side(self, side_name, rot_degree):
        self.action_trigger = False
        cube_position = self.cubes_side_positons[side_name]
        rotation_axis = self.rotation_axes[side_name]
        self.reparent_to_scene()
        for cube in self.CUBES:
            if cube.position in cube_position:
                cube.parent = self.PARENT
        if abs(rot_degree) == 90 and self.solve_cube == True:
            eval(f'self.PARENT.animate_rotation_{rotation_axis}(rot_degree, duration = self.animation_time, curve = curve.linear)')
            invoke(self.toggle_animation_trigger, delay = self.animation_time + 0.2)
        elif abs(rot_degree) == 180 and self.solve_cube == True:
            pass
            eval(f'self.PARENT.animate_rotation_{rotation_axis}(rot_degree/2, duration = self.animation_time, curve = curve.linear)')
            invoke(self.second_move,rotation_axis, rot_degree, delay = self.animation_time + 0.2)
            invoke(self.toggle_animation_trigger, delay = self.animation_time*2 + 0.4)
        else:
            eval(f'self.PARENT.animate_rotation_{rotation_axis}(rot_degree, duration = self.animation_time, curve = curve.linear)')
            invoke(self.toggle_animation_trigger, delay = self.animation_time + 0.2)

    def second_move(self, rotation_axis, rot_degree):
        eval(f'self.PARENT.animate_rotation_{rotation_axis}(rot_degree, duration = self.animation_time, curve = curve.linear)')

    def reparent_to_scene(self):
        for cube in self.CUBES:
            if cube.parent == self.PARENT:
                world_pos, world_rot = round(cube.world_position, 1), cube.world_rotation
                cube.parent = scene
                cube.position, cube.rotation = world_pos, world_rot
        self.PARENT.rotation = 0
        
    def camera_movement(self):
        if held_keys['a']:
            self.CAMERA_PARENT.rotation_y += 1.3
        if held_keys['d']:
            self.CAMERA_PARENT.rotation_y -= 1.3
        if held_keys['w']:
            self.CAMERA_PARENT.rotation += (1.3, 0, 1.3)
        if held_keys['s']:
            self.CAMERA_PARENT.rotation -= (1.3, 0, 1.3)

    def scramblee_cube(self):
        if self.action_trigger and self.index1 < len(self.reverse_sol) and self.scramble_cube:
            self.animation_time = 0
            self.rotate_side(self.moves_dict[self.reverse_sol[self.index1]][0], self.moves_dict[self.reverse_sol[self.index1]][1])
            self.index1 += 1
            if self.index1 == len(self.reverse_sol):
                self.animation_time = 0.6
                self.index1 += 1
                self.scramble_cube = False
                self.loading_text.text = "Hit SPACE-BAR to auto solve"
                self.loading_text.y = -0.4
                self.loading_text.x = -0.3
                for cube in self.CUBES : cube.visible = True
                for text in self.move_text: text.visible = True
                self.num_moves.visible = self.next_button.visible = self.back_button.visible = self.solve_cube = True

    def next_move(self):
        self.animation_time = 0.5
        if self.solve_cube and self.index2 < len(self.solution) and self.action_trigger:
            self.rotate_side(self.moves_dict[self.solution[self.index2]][0], self.moves_dict[self.solution[self.index2]][1])
            self.index2 += 1
        if self.index2 == len(self.solution):
            self.loading_text.text = "#   Rubik's Cube Solved   #"
        else:
            self.loading_text.text = "Hit SPACE-BAR to auto solve"
    
    def back_move(self):
        self.animation_time = 0.3
        if self.solve_cube and self.index2 > 0 and self.action_trigger:
            self.rotate_side(self.moves_dict[self.reverse_sol[len(self.reverse_sol)-self.index2]][0], self.moves_dict[self.reverse_sol[len(self.reverse_sol)-self.index2]][1])
            self.index2 -= 1
        if self.index2 == len(self.solution):
            self.loading_text.text = "#   Rubik's Cube Solved   #"
        else:
            self.loading_text.text = "Hit SPACE-BAR to auto solve"

    def update(self):
        if self.scramble_cube:
            self.scramblee_cube()

        self.camera_movement()

        if self.index2 >= 0 and self.index2 <= len(self.solution):
            for text in self.move_text:
                text.color = color.white
                text.scale = 1
                text.y = 0.45
            if self.index2 != 0:
                self.move_text[self.index2-1].color = color.yellow
                self.move_text[self.index2-1].scale = 2
                self.move_text[self.index2-1].y = 0.46

        if self.solve_cube_auto:
            self.next_move()

        if self.index2 < len(self.solution) and self.solve_cube:
            self.next_button.visible = True
        else:
            self.next_button.visible = False
        
        if self.index2 > 0 and self.solve_cube:
            self.back_button.visible = True
        else:
            self.back_button.visible = False

        if self.CAMERA_PARENT.rotation_x >= 360:
            self.CAMERA_PARENT.rotation_x = 0
        if self.CAMERA_PARENT.rotation_y >= 360:
            self.CAMERA_PARENT.rotation_y = 0
        if self.CAMERA_PARENT.rotation_z >= 360:
            self.CAMERA_PARENT.rotation_z = 0
    
    def input(self,key):
        if key == 'space':
            self.solve_cube_auto = True
        if key == 'n':
            self.solve_cube_auto = False
            self.next_move()
        if key == 'b':
            self.solve_cube_auto = False
            self.back_move()
        if key == 'r':
            self.CAMERA_PARENT.animate_rotation_x(0, duration = 1)
            self.CAMERA_PARENT.animate_rotation_y(0, duration = 1)
            self.CAMERA_PARENT.animate_rotation_z(0, duration = 1)
        super().input(key)

if __name__ == '__main__':

    #cube_color = 'byobybbrororbbobrgyyywrowrygwgggobggwgwyoyrgorbowwwwry'
    #solution = utils.solve(cube_color, 'Kociemba')
    #solution = [ str(x) for x in solution]
    solution = ['U', "F'", "L'", "D'", 'L2', "U'", 'F', "B'", 'U', 'B', "R'", 'F', 'U2', 'R2', 'B2', 'U', 'B2', 'D', 'B2', 'U2', "D'", 'B2']
    print(solution)
    # Rubik 3D starts here
    game = Game(solution1 = solution)
    def update():
        game.update()
    game.run()