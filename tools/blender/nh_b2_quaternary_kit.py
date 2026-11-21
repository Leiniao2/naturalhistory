"""
Small helpers shared by the batch-2 Quaternary species scripts (tag "b2_quaternary").

  * repaint(obj, fn): recolours a finished object's "Col" corner colours in place with
    fn(co, normal, rgb) -> rgb, for markings the shared body-plan builders can't paint
    (an emperor penguin's ear patches, a snowy owl's speckles, an orca's eye patch...).
  * wrap_run(build, name, **preview): like nh_model.run, for scripts that post-process
    a shared builder's object before it is exported.
"""

import nh_model as nh


def repaint(obj, fn):
    me = obj.data
    attr = me.color_attributes.get("Col")
    if attr is None:
        return obj
    me.calc_loop_triangles()
    verts = me.vertices
    if attr.domain == "CORNER":
        for li, loop in enumerate(me.loops):
            v = verts[loop.vertex_index]
            c = attr.data[li].color
            nc = fn(v.co, v.normal, (c[0], c[1], c[2]))
            if nc is not None:
                attr.data[li].color = (nc[0], nc[1], nc[2], 1.0)
    else:
        for vi, v in enumerate(verts):
            c = attr.data[vi].color
            nc = fn(v.co, v.normal, (c[0], c[1], c[2]))
            if nc is not None:
                attr.data[vi].color = (nc[0], nc[1], nc[2], 1.0)
    return obj


def wrap_run(build, name, **preview):
    nh.run(build, name, **preview)
