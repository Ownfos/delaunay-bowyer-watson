import turtle

# t and s are global variables, which can be obtained
# from turtle.getturtle() and turtle.getscreen() respectively.
# although this is not a good pratice, I think it is enough for a prototype.

def drawLine(p1, p2):
    t.penup()
    t.goto(p1)
    t.pendown()
    t.goto(p2)
    s.update()


def drawPoint(p):
    t.penup()
    t.goto(p)
    t.dot()
    s.update()


def drawCircle(p, r):
    t.penup()

    # by default, the circle is placed above the turtle by offset of r
    # that's why we need positional adjustment for the circle to be on point p exactly
    x, y = p
    t.goto((x, y-r))
    
    t.pendown()
    t.circle(r)
    s.update()


def clearScreen():
    s.reset()
    t.hideturtle()


# datatype overview:
# 1. all points and vectors are handled as tuples
# ex) 2d vector -> (x, y)
#     3d vector -> (x, y, z)
# 2. triangles and edges are tuples of points, where the order of the points is arbitrary
# ex) triangle -> (p1, p2, p3)
#     edge -> (p1, p2)

def vecDiff2D(p1, p2):
    return (p1[0] - p2[0], p1[1] - p2[1])


def vecDiff3D(p1, p2):
    return (p1[0] - p2[0], p1[1] - p2[1], p1[2] - p2[2])


def vecCross2D(p1, p2, p3):
    """
    returns the cross product between p1->p2 vector and p1->p3 vector
    """
    v1 = vecDiff2D(p2, p1) # p2 - p1
    v2 = vecDiff2D(p3, p1) # p3 - p1
    return v1[0] * v2[1] - v1[1] * v2[0]


def planePoint(p):
    """
    converts (x, y) to a point on a 3d surface (x, y, x^2 + y^2)
    """
    return (p[0], p[1], p[0]*p[0] +p[1]*p[1])


def ccw(p1, p2, p3):
    """
    returns true iff p1->p2 vector and p1->p3 vector are in counter-clockwise position
    """
    return vecCross2D(p1, p2, p3) > 0


def isInCircum(p, p1, p2, p3):
    """
    returns true iff p is in the circumcircle of triangle (p1,p2,p3)
    """
    p = planePoint(p)
    p1 = planePoint(p1)
    p2 = planePoint(p2)
    p3 = planePoint(p3)

    v1 = vecDiff3D(p1, p) # p1 - p
    v2 = vecDiff3D(p2, p) # p2 - p
    v3 = vecDiff3D(p3, p) # p3 - p

    # the volume of tetrahedron (p, p1, p2, p3) where each points are the "plane points".
    # iff p is outside, planePoint(p) is below the plane containing p1, p2, p3 on 3d space
    # and therefore the determinent positive, given that p1, p2, p3 are in counter-clockwise order.
    det = v1[0] * (v2[1] * v3[2] - v2[2] * v3[1]) - v1[1] * (v2[0] * v3[2] - v2[2] * v3[0]) + v1[2] * (v2[0] * v3[1] - v2[1] * v3[0])

    if ccw(p1, p2, p3):
        return det > 0
    else:
        return det < 0


def validate(triangles):
    for t in triangles:
        # check if the triangulation has a triangle that contains another point in its circumcircle
        for p in pointList:
            if p not in t and isInCircum(p, t[0], t[1], t[2]):
                return False
    return True


def triangulate(pointList):
    """
    returns the Delaunay Triangulation using Bowyer-Watson algorithm
    """
    triangles = [] # the resulting triangle mesh
    
    # insert super triangle
    bignum = 100000
    supertriangle = ((-bignum, -bignum), (bignum, -bignum), (0, bignum))
    triangles.append(supertriangle)

    # incrementally insert point and retriangulate 'bad triangles'
    for p in pointList:
        badTriangles = []
        badEdges = set()
        for t in triangles:
            # find all triangles where its circumcircle contains the new point p.
            # the 'bad triangles' will form a star-shaped polygon.
            if isInCircum(p, t[0], t[1], t[2]):
                badTriangles.append(t)
                # keep track of the star-shaped polygon's boundary.
                # since each edge is shared by two triangles,
                # duplicate insertion implies that this edge is not on the boundary.
                edges = [(t[0], t[1]), (t[1], t[0]), (t[1], t[2]), (t[2], t[1]), (t[0], t[2]), (t[2], t[0])] # three edges in both directions
                for i in range(0, 3):
                    # since the order of points in an edge is arbitrary, we need to search for either p1->p2 or p2->p1
                    edgeAndReverse = {edges[i*2], edges[i*2+1]}
                    if len(badEdges.intersection(edgeAndReverse)) == 0:
                        badEdges.add(edges[i*2])
                    else:
                        badEdges = badEdges.difference(edgeAndReverse)

        # now remove bad triangles to create star-shaped polygon hole
        for t in badTriangles:
            triangles.remove(t)
        
        # insert new triangulation for the hole
        for edge in badEdges:
            triangles.append((edge[0], edge[1], p))

    # after inserting all points, remove triangles connected to the supertriangle
    badTriangles = []
    for t in triangles:
        # check if any of the three vertices are shared with the supertriangle
        for i in range(0, 3):
            if t[i] in supertriangle:
                badTriangles.append(t)
                break
    for t in badTriangles:
        triangles.remove(t)

    # confirm that we don't have any bad triangles
    if validate(triangles) == False:
        raise RuntimeError('Invalid triangulation!!!')

    return triangles

                   

def renderTriangulation(triangles):
    clearScreen()
    for p in pointList:
        drawPoint(p)
    for t in triangles:
        drawLine(t[0], t[1])
        drawLine(t[1], t[2])
        drawLine(t[2], t[0])


def addPoint(x, y):
    p = (x, y)
    pointList.append(p)
    drawPoint(p)
    if len(pointList) >= 3:
        renderTriangulation(triangulate(pointList))


def undo():
    if len(pointList) > 0:
        pointList.pop()
        if len(pointList) >= 3:
            renderTriangulation(triangulate(pointList))


def reset():
    pointList.clear()
    clearScreen()


# initialize turtle
t = turtle.getturtle()
s = turtle.getscreen()
s.tracer(False)
s.onclick(addPoint)
s.onkey(undo, 'q')
s.onkey(reset, 'r')
clearScreen()

# initialze triangulation setting
pointList = []

# run
s.listen()
turtle.mainloop()



