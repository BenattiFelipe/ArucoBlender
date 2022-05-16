import numpy as np
import bpy
import os
def creat_wall(name, wall_dic):
    w,h,t,location,ang = wall_dic[name]
    import bpy, bmesh, os
    rotation = ( 0, 0, np.deg2rad(ang))
    bpy.ops.mesh.primitive_cube_add(size=1, location = location, rotation = rotation)
    ob = bpy.context.object
    ob.name = name
    ob.dimensions = (w, t, h)

def creat_aruco(file_path, img_aruco, name, scale = (0.1,0.2,0.1), location=(0,-0.1,0), value = (1,1,1)):
    import bpy, bmesh, os
    file = file_path+"/"+img_aruco
    bpy.ops.mesh.primitive_cube_add()
    ob = bpy.context.object
    bpy.ops.object.mode_set(mode = 'OBJECT')
    bpy.ops.transform.resize(use_proportional_edit=True, value=scale)
    bpy.context.object.location = location
    #bpy.context.object.scale = scale
    bpy.context.object.dimensions = scale
    bpy.ops.object.transform_apply(location=True, rotation=False, scale=True, properties=True)
    bpy.context.object.name = name
    


    bpy.ops.object.mode_set(mode = 'EDIT')
    #    ob = bpy.context.object


    mat = bpy.data.materials.new(name="mat{}".format(name))
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs[3].default_value = (0, 0, 0, 1)
    bsdf.inputs[19].default_value = (0, 0, 0, 1)
    bsdf.inputs[9].default_value = 0
    bsdf.inputs[7].default_value = 0
    bsdf.inputs[13].default_value = 0
    
    texImage = mat.node_tree.nodes.new('ShaderNodeTexImage')
    texImage.image = bpy.data.images.load(file)
    texImage.location = -300, 120
    mat.node_tree.links.new(bsdf.inputs['Base Color'], texImage.outputs['Color'])
    if ob.data.materials:
        ob.data.materials[0] = mat
    else:
        ob.data.materials.append(mat)

     
    bm = bmesh.from_edit_mesh(ob.data)
     
    bm.select_mode = {'FACE'}
    bpy.ops.mesh.select_all(action='DESELECT')
    bm.faces.ensure_lookup_table()
    for face in bm.faces:
        face.select_set(True) 
        bpy.ops.uv.unwrap()
        face.select_set(False)
    
    bpy.ops.object.mode_set(mode='OBJECT')

def add_aruco(aruco, dic,s, wp, hp, tp, lp, angp, qnt, t, pontas, file_path_aruco):
    if len(aruco.keys()) == 0:
        aruco.update({"grp":{}})
        new_grp = 0
    if not len(aruco['grp']) == 0:
        grp_value = aruco["grp"].value()
        last_grp = grp_value[-1]
        new_grp = last_grp + 10
    m = int(round(wp/s))
    n = int(round(hp/s))
    if qnt<m and qnt<10:
        ids = [i for i in range(1,qnt+1)]
        aruco['grp'].update({new_grp:ids})
        a = (wp/(1+qnt))
        if angp == 0:
            x = [lp[0]+a*i-wp/2 for i in range(1,qnt+1)]
            y = [lp[1] for i in range(qnt)]
        else:
            x = [lp[0] for i in range(qnt)]
            y = [lp[1]+a*i-wp/2 for i in range(1,qnt+1)]
        for i in range(len(x)):
            dic.update({f'A{ids[i]}':"A"})
            aruco.update({f'A{ids[i]}': (ids[i], s, (x[i],-0.01, y[i]), angp)})
    return aruco ,dic

def draw(dic, wall_dic, aruco, file_path, th=0.1):
    for name in dic.keys():
        if dic[name] == "W":
            creat_wall(name, wall_dic)
        if dic[name] == "A":
            id, s, location, ang = aruco[name]
            scale = (s,th,s)
            img_aruco = "marker{}.png".format(id)
            creat_aruco(file_path, img_aruco, name, scale, location)

        

def write_loop(dic, wall_dic, aruco, th = 0.1, file_path_aruco = "//..\\ArucoPath"):
    obj = input("Qual objeto quer adicionar: \n('A' - Aruco)\n('W' - Wall)\n('D' - Draw):\n")
    if obj == 'W':
        if len(wall_dic.keys()) == 0:
            name = input("Qual o nome da parede: ")
            dic.update({name:"W"})
            w = float(input("Qual a largura da parede: "))
            h = float(input("Qual a altura da parede: "))
            # print_wall(wall_dic)
            ang = 0
            loc = (0,0,0)
        else:
            name = input("Qual o nome da parede: ")
            dic.update({name:"W"})
            p = input("Qual a parede que quer adicionar: ")
            if p not in wall_dic.keys():
                print("Parede não encontrada")
                return write_loop(dic, wall_dic, aruco, th)
            w = float(input("Qual a largura da parede: "))
            h = float(input("Qual a altura da parede: "))
            # print_wall(wall_dic)
            wp, hp, tp, lp, angp = wall_dic[p]
            l0,l1,l2=(0,0,0)
            if angp == 90 :
                ang = 0
                s1 = int(input("Pela borda da (0)Esquerda (1)Direita: "))
                if s1 == 0:
                    s1 = -1
                l0 = lp[0]+ s1*(w/2 + tp/2)
                s2 = int(input("Pela borda da (0)Baixo (1)Cima: "))
                if s2 == 0:
                    s2 = -1
                l1 = lp[1] + s2*(wp/2 + th/2)
            if angp == 0 :
                ang = 90
                s1 = int(input("Pela borda da (0)Esquerda (1)Direita: "))
                if s1 == 0:
                    s1 = -1
                l0 = lp[0] + s1*(wp/2 + th/2)
                s2 = int(input("Orientação (0)Baixo (1)Cima: "))
                if s2 == 0:
                    s2 = -1
                l1 = lp[1] + s2*(w/2 + tp/2)
            loc = (l0,l1,l2)
        wall_dic.update({name: (w, h, th, loc, ang)})
    elif obj == 'A':
        p = input("Qual a parede que quer adicionar: ")
        if p not in wall_dic.keys():
            print("Parede não encontrada")
            return write_loop(dic, wall_dic, aruco, th)
        wp, hp, tp, lp, angp = wall_dic[p]
        s = float(input("Qual o tamanho do aruco: "))
        qnt = int(input("Quantos Arucos Deseja Adicionar: "))
        t = int(input("Uniforme(0) ou Aleatorio(1): "))
        pontas = input("Aruco marcado extremidades Sim(0) ou Não(1): ")
        aruco, dic = add_aruco(aruco, dic, s, wp, hp, tp, lp, angp, qnt, t, pontas, file_path_aruco)
        print(aruco)
        return (dic, wall_dic, aruco)
    elif obj == 'D':
        return (dic, wall_dic, aruco)
    return (dic, wall_dic, aruco)

def find_line(p0,p1):
    x0,y0,z0 = p0
    x1,y1,z1 = p1
    if x1!=x0:
        a = (z1-z0)/(x1-x0)
    b = a*x0 - z0
    return a,b

def path_camera_aruco(aruco, camera_pos, n):
    p = []
    cont = 0
    for name in aruco.keys():
        if name != 'grp':
            id, s, location, ang = aruco[name]
            if cont>0:
                a,b = find_line(location0,location)
                x = np.linspace(location0[0],location[0],n)
                print(x)
                for i in x:
                    z = (a*i+b)
                    p.append((i,camera_pos[1],z))
            else:
                x,y,z = location
                p.append((x,camera_pos[1],z))
                cont+=1
            location0 = location
    return p

def render_img(scene, file_path, filename, extension):
    bpy.context.scene.render.filepath = os.path.join(file_path,('{0}.{1}'.format(filename,extension)))# (output_file_pattern_string % str(i)))
    bpy.ops.render.render(write_still = True)
    print('{0}.{1}'.format(filename,extension))

def mov_camera(camera, p, scene, file_path, filename, extension="PNG"):
    for i in range(len(p)):
        camera.location = p[i]
        render_img(scene, file_path, filename+str(i), extension)

def delete_all(camera, light):
    bpy.ops.object.select_all(action='SELECT')
    camera.select_set(False)
    light.select_set(False)
    bpy.ops.object.delete()
        

def main():
    camera = bpy.data.objects['Camera.003']
    light = bpy.data.objects['Light.003']
    file_path = 'Users/NOTE 2/IC/Aruco_Blendder/video/mov'
    filename = "mov"
    dic = {}
    wall_dic = {}
    aruco = {}
    while True:
        dic, wall_dic, aruco = write_loop(dic, wall_dic, aruco)
        print(wall_dic)
        print("Deseja continuar? (S/N/")
        cont = input()
        if cont == 'N':
            break
    draw(dic, wall_dic, aruco, file_path = "//..\\ArucoPath")
    camera = bpy.data.objects['Camera.003']
    scene = bpy.context.scene
    scene.render.image_settings.file_format='PNG'
    p = path_camera_aruco(aruco, camera.location, 4)
    mov_camera(camera,p,scene,file_path,filename)
#    delete_all(camera, light)
    
if __name__ == '__main__':
    main()
    