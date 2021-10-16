"""
 Make Soft IK - A script to stop IK systems from snapping when reaching their final position.

 Math by by Andrew Nicholas - www.andynicholas.com
 GUI inspired by https://github.com/TrevisanGMW/gt-tools

@AndySedano
"""

import maya.cmds as cmds
import sys

settings = {'ik_handle': '', 'attr_holder': ''}


def build_gui():
    window_name = "Soft_IK"
    if cmds.window(window_name, exists=True):
        cmds.deleteUI(window_name)

    gui_soft_ik = cmds.window(window_name, title="Soft IK",
                              titleBar=True, mnb=False, mxb=False, sizeable=True)

    cmds.window(window_name, e=True, s=True, wh=[1, 1])

    content_main = cmds.columnLayout(adj=True)

    title_bgc_color = (.4, .4, .4)
    cmds.separator(h=10, style='none')  # Empty Space
    cmds.rowColumnLayout(nc=1, cw=[(1, 270)], cs=[
                         (1, 10)], p=content_main)  # Window Size Adjustment
    cmds.text("   Soft IK", bgc=title_bgc_color,
              fn="boldLabelFont", align="left", h=20)
    cmds.separator(h=5, style='none')  # Empty Space

    # Body ====================
    body_column = cmds.rowColumnLayout(
        nc=1, cw=[(1, 260)], cs=[(1, 10)], p=content_main)

    cmds.text(l='This script stops an IK setup from snapping.',
              align="center", fn='boldLabelFont')
    cmds.separator(h=5, style='none')  # Empty Space
    cmds.text(l='Load an ikHandle and click on "Make Soft IK"', align="center")
    cmds.separator(h=5, style='none')  # Empty Space
    cmds.text(l='By default the attribute holder determines the\n stretch, If no attribute holder is selected, a \ndefault control will be made.', align="center")
    cmds.separator(h=10, style='none')  # Empty Space

    ik_handle_container = cmds.rowColumnLayout(
        nc=2, cw=[(1, 129), (2, 130)], cs=[(1, 0)])
    ik_handle_btn = cmds.button(
        l="Load IK Handle", c=lambda x: object_load_handler("ik_handle"), w=130)
    ik_handle_status = cmds.button(l="Not loaded yet", bgc=(.2, .2, .2), w=130,
                                   c=lambda x: select_existing_object(settings.get('ik_handle')))

    attr_holder_container = cmds.rowColumnLayout(
        nc=2, cw=[(1, 129), (2, 130)], cs=[(1, 0)], p=body_column)
    attr_holder_btn = cmds.button(
        l="Load Attribute Holder", c=lambda x: object_load_handler("attr_holder"), w=130)
    attr_holder_status = cmds.button(l="Not loaded yet", bgc=(.2, .2, .2), w=130,
                                     c=lambda x: select_existing_object(settings.get('attr_holder')))

    cmds.rowColumnLayout(nc=1, cw=[(1, 260)], cs=[(1, 10)], p=content_main)

    cmds.separator(h=7, style='none')  # Empty Space
    cmds.separator(h=5)
    cmds.separator(h=7, style='none')  # Empty Space

    cmds.button(l="Make Soft IK", bgc=(.6, .6, .6),
                c=lambda x: validate_operation())
    cmds.separator(h=10, style='none')  # Empty Space

    # Show and Lock Window
    cmds.showWindow(gui_soft_ik)
    cmds.window(window_name, e=True, s=False)

    cmds.setFocus(window_name)

    def object_load_handler(operation):
        """Fucntion to handle load buttons

        Args:
            operation (string): String to determine function
        """

        if operation == 'ik_handle':

            # Get the selected object
            sel = cmds.ls(selection=True, long=True)

            if(len(sel) == 0 or cmds.nodeType(sel[0]) != 'ikHandle'):
                cmds.warning("Please select an ikHandle")
                cmds.button(ik_handle_status, l="Failed to Load",
                            e=True, bgc=(1, .4, .4), w=130)
            else:
                settings['ik_handle'] = sel[0]
                cmds.button(ik_handle_status, l=settings.get(
                    'ik_handle'), e=True, bgc=(.6, .8, .6), w=130)

        if operation == 'attr_holder':
            sel = cmds.ls(selection=True, long=True)

            if(len(sel) == 0):
                cmds.warning("Nothing selected")
                settings['attr_holder'] = ''
                cmds.button(attr_holder_status, l="Not provided",
                            e=True, bgc=(.2, .2, .2), w=130)
            elif cmds.objExists(sel[0]):
                settings['attr_holder'] = sel[0]
                cmds.button(attr_holder_status, l=settings.get(
                    'attr_holder'), e=True, bgc=(.6, .8, .6), w=130)

    def validate_operation():
        """Function to verify all variables are in place before creating the soft IK
        """

        is_valid = False
        attr_holder = None

        # Validate ikHandle
        if settings.get('ik_handle') == '':
            cmds.warning(
                'Please load an ikHandle first before running the script.')
            is_valid = False
        else:
            if cmds.objExists(settings.get('ik_handle')):
                is_valid = True
            else:
                cmds.warning("{0} couldn\'t be located. Make sure you didn\'t rename or deleted the object after loading it".format(
                    str(settings.get('ik_handle'))))

        # Validate Attribute Holder
        if is_valid:
            if settings.get('attr_holder') != '':
                if cmds.objExists(settings.get('attr_holder')):
                    attr_holder = settings.get('attr_holder')
                else:
                    cmds.warning("{0} couldn\'t be located. Make sure you didn\'t rename or deleted the object after loading it. A simpler version of the stretchy system was created.'".format(
                        str(settings.get('attr_holder'))))
            else:
                sys.stdout.write(
                    'An attribute holder was not provided. A default control was created.')

        # Run Script
        if is_valid:
            make_soft_ik(settings.get('ik_handle'),
                         attribute_holder=attr_holder)
            cmds.deleteUI(window_name, window=True)


def select_existing_object(obj):
    """Selects an existing object in case it exists

    Args:
        obj (str): Name of the object
    """

    if obj != '':
        if cmds.objExists(obj):
            cmds.select(obj)
        else:
            cmds.warning(
                "{} couldn\'t be selected. Make sure you didn\'t rename or deleted the object after loading it".format(str(obj)))
    else:
        cmds.warning(
            'Nothing loaded. Please load an object before attempting to select it.')


def make_soft_ik(ik_handle, attribute_holder=None):
    # Main method, creates the whole soft effector system, controls, nodes, etc

    # From the ikHandle get the start and end nodes
    start_joint = cmds.listConnections('{}.startJoint'.format(ik_handle))[0]
    end_effector = cmds.listConnections('{}.endEffector'.format(ik_handle))[0]

    length_node = distance_between_ik_chain(start_joint, end_effector)

    ##### Create and parent controls #####

    # Circle main controller
    ctrl = cmds.circle(name="softIK_Ctrl#")[0]
    cmds.matchTransform(ctrl, ik_handle)

    if(attribute_holder == None):
        attribute_holder = ctrl

    add_control_attributes(attribute_holder)

    cmds.connectAttr('{}.output'.format(length_node),
                     '{}.ChainLength'.format(attribute_holder), lock=False)
    cmds.setAttr('{}.ChainLength'.format(attribute_holder), lock=True)

    # Aim locator that aims at the start joint
    aim_lctr = cmds.spaceLocator(name="aim_Lctr#")[0]
    cmds.matchTransform(aim_lctr, ctrl)
    cmds.parent(aim_lctr, ctrl)
    cmds.makeIdentity(aim_lctr)
    cmds.setAttr('{}Shape.visibility'.format(aim_lctr), 0)

    # Parent the ik handle to the aim locator
    ik_handle = cmds.parent(ik_handle, aim_lctr)[0]

    # Length locator the find the working legnth of the ik chain
    length_lctr = cmds.spaceLocator(name="length_Lctr#")[0]
    cmds.matchTransform(length_lctr, ctrl)
    cmds.parent(length_lctr, ctrl)
    cmds.setAttr('{}Shape.visibility'.format(length_lctr), 0)

    cur_distance = create_distance_nodes(start_joint, length_lctr)

    cmds.aimConstraint(start_joint, aim_lctr, maintainOffset=True,
                       aimVector=(0, 0, 1), upVector=(0, 1, 1))

    # Formula by Andrew Nicholas - www.andynicholas.com
    # d_soft (1 - e^(-(x-d_a)/d_soft))+d_a
    # d_a = chain_distance - d_soft

    # Calculate da
    da = cmds.shadingNode('floatMath', asUtility=True, name="da#")
    cmds.connectAttr('{}.output'.format(length_node), '{}.floatA'.format(da))
    cmds.connectAttr('{}.SoftDistance'.format(
        attribute_holder), '{}.floatB'.format(da))
    cmds.setAttr('{}.operation'.format(da), 1)

    # Calculate x - da
    x_minus_da = cmds.shadingNode(
        'floatMath', asUtility=True, name="x_minus_da#")
    cmds.connectAttr('{}.distance'.format(cur_distance),
                     '{}.floatA'.format(x_minus_da))
    cmds.connectAttr('{}.outFloat'.format(da),
                     '{}.floatB'.format(x_minus_da))
    cmds.setAttr('{}.operation'.format(x_minus_da), 1)

    # Multiply by -1
    mult_minus_one = cmds.shadingNode(
        'floatMath', asUtility=True, name="mult_minus_one#")
    cmds.connectAttr('{}.outFloat'.format(x_minus_da),
                     '{}.floatA'.format(mult_minus_one))
    cmds.setAttr('{}.floatB'.format(mult_minus_one), -1)
    cmds.setAttr('{}.operation'.format(mult_minus_one), 2)

    # Divide by softDistance
    div_soft = cmds.shadingNode(
        'floatMath', asUtility=True, name="div_soft#")
    cmds.connectAttr('{}.outFloat'.format(mult_minus_one),
                     '{}.floatA'.format(div_soft))
    cmds.connectAttr('{}.SoftDistance'.format(attribute_holder),
                     '{}.floatB'.format(div_soft))
    cmds.setAttr('{}.operation'.format(div_soft), 3)

    # Exponent
    exponent = cmds.shadingNode(
        'floatMath', asUtility=True, name="exponent#")
    cmds.connectAttr('{}.outFloat'.format(div_soft),
                     '{}.floatB'.format(exponent))
    cmds.setAttr('{}.floatA'.format(exponent), 2.71828)
    cmds.setAttr('{}.operation'.format(exponent), 6)

    # 1 minus exponent
    one_minus_exp = cmds.shadingNode(
        'floatMath', asUtility=True, name="one_minus_exp#")
    cmds.connectAttr('{}.outFloat'.format(exponent),
                     '{}.floatB'.format(one_minus_exp))
    cmds.setAttr('{}.operation'.format(one_minus_exp), 1)

    # mult by soft
    mult_soft = cmds.shadingNode(
        'floatMath', asUtility=True, name="mult_soft#")
    cmds.connectAttr('{}.outFloat'.format(one_minus_exp),
                     '{}.floatA'.format(mult_soft))
    cmds.connectAttr('{}.SoftDistance'.format(attribute_holder),
                     '{}.floatB'.format(mult_soft))
    cmds.setAttr('{}.operation'.format(mult_soft), 2)

    # Add da
    plus_da = cmds.shadingNode(
        'floatMath', asUtility=True, name="plus_da#")
    cmds.connectAttr('{}.outFloat'.format(mult_soft),
                     '{}.floatA'.format(plus_da))
    cmds.connectAttr('{}.outFloat'.format(da),
                     '{}.floatB'.format(plus_da))

    # Distance minus result
    dist_minus_res = cmds.shadingNode(
        'floatMath', asUtility=True, name="dist_minus_res#")
    cmds.connectAttr('{}.distance'.format(cur_distance),
                     '{}.floatA'.format(dist_minus_res))
    cmds.connectAttr('{}.outFloat'.format(plus_da),
                     '{}.floatB'.format(dist_minus_res))
    cmds.setAttr('{}.operation'.format(dist_minus_res), 1)

    # Condition Length
    length_cond = cmds.shadingNode(
        'condition', asUtility=True, name="length_cond#")
    cmds.connectAttr('{}.distance'.format(cur_distance),
                     '{}.firstTerm'.format(length_cond))
    cmds.connectAttr('{}.outFloat'.format(da),
                     '{}.secondTerm'.format(length_cond))
    cmds.setAttr('{}.operation'.format(length_cond), 5)

    # Condition Multiply
    cond_mult = cmds.shadingNode(
        'floatMath', asUtility=True, name='cond_mult#')
    cmds.connectAttr('{}.outFloat'.format(dist_minus_res),
                     '{}.floatA'.format(cond_mult))
    cmds.connectAttr('{}.outColorR'.format(length_cond),
                     '{}.floatB'.format(cond_mult))
    cmds.setAttr('{}.operation'.format(cond_mult), 2)

    # On/Off Condition
    off_cond = cmds.shadingNode(
        'floatCondition', asUtility=True, name="off_cond#")
    cmds.connectAttr('{}.SoftIK'.format(attribute_holder),
                     '{}.condition'.format(off_cond))
    cmds.connectAttr('{}.outFloat'.format(cond_mult),
                     '{}.floatA'.format(off_cond))
    cmds.setAttr('{}.floatB'.format(off_cond), 0)

    # Connect result condition to the ik handle translate Z
    cmds.connectAttr('{}.outFloat'.format(off_cond),
                     '{}.tz'.format(ik_handle))


def add_control_attributes(ctrl):
    """Adds the attributes required to control the chain
        - Turn On/Off the soft effect
        - Distance to begin the soft effect
        - Show the length of the chain

    Args:
        ctrl (string): Name of the controller
    """

    cmds.addAttr(ctrl, longName="SoftIK", attributeType='bool',
                 keyable=True, defaultValue=1)
    cmds.addAttr(ctrl, longName="ChainLength",
                 attributeType='float', keyable=True)
    cmds.addAttr(ctrl, longName="SoftDistance",
                 attributeType='float', keyable=True)
    cmds.setAttr('{}.SoftDistance'.format(ctrl), .5)


def distance_between_ik_chain(first, last):
    """ Calculates the max distance of the ik chain

    Args:
        first (string): Name of the first element to measure
        last (string): Name of the last element to measure

    Returns:
        string: Name of the distance node
    """
    cur_node = last
    parent = cmds.listRelatives(cur_node, parent=True)[0]
    total_distance_node = None
    sum_node = None

    while(parent != first):
        distance_node = create_distance_nodes(cur_node, parent)

        cur_sum_node = cmds.shadingNode('addDoubleLinear', asUtility=True)
        cmds.connectAttr('{}.distance'.format(distance_node),
                         '{}.input1'.format(cur_sum_node), force=True)

        if(sum_node != None):
            cmds.connectAttr('{}.output'.format(cur_sum_node),
                             '{}.input2'.format(sum_node), force=True)
        else:
            total_distance_node = cur_sum_node

        sum_node = cur_sum_node
        cur_node = parent
        parent = cmds.listRelatives(cur_node, parent=True)[0]

    distance_node = create_distance_nodes(cur_node, first)
    cmds.connectAttr('{}.distance'.format(distance_node),
                     '{}.input2'.format(sum_node), force=True)

    return total_distance_node


def create_distance_nodes(first, second):
    """Generates all the nodes required to calculate the distance between objects
        https://williework.blogspot.com/2011/10/creating-nice-clean-distance-node-using.html

    Args:
        first (string): Name of the first node
        second (string): Name of the second node

    Returns:
        string: Name of the distance node
    """

    distance_node = cmds.shadingNode('distanceBetween', asUtility=True)
    cmds.connectAttr('{}.rotatePivotTranslate'.format(first),
                     '{}.point2'.format(distance_node), force=True)
    cmds.connectAttr('{}.worldMatrix[0]'.format(first),
                     '{}.inMatrix2'.format(distance_node), force=True)
    cmds.connectAttr('{}.rotatePivotTranslate'.format(second),
                     '{}.point1'.format(distance_node), force=True)
    cmds.connectAttr('{}.worldMatrix[0]'.format(second),
                     '{}.inMatrix1'.format(distance_node), force=True)

    return distance_node


# create_soft_effector()
build_gui()
