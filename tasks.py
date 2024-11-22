from celery import Celery
from models import User, Group
from database import db

from sqlalchemy import func
group_map = {}  # In-memory data structure: {group_id: set(attributes)}

def initialize_group_map():
    """
    Initialize the in-memory group_map from the database.
    This function should be called at application startup.
    """
    global group_map
    group_map = {}

    # Load all groups from the database
    groups = Group.query.all()
    for group in groups:
        group_map[group.id] = set(group.attributes)  # Ensure attributes are stored as sets

def assign_group(user_id, attributes, minimum_matching_threshold=3):
    """
    Assign a user to a group based on matching attributes. If no group satisfies the 
    threshold, a new group is created.
    
    :param user_id: ID of the user to assign.
    :param attributes: List of attributes for the user.
    :param minimum_matching_threshold: Minimum number of matching attributes to consider a group.
    """
    global group_map
    
    # Convert user attributes to a set for efficient comparison
    user_attributes_set = set(attributes)
    
    best_group = None
    max_matching_attributes = 0

    # Iterate over all groups in the in-memory group_map
    for group_id, group_attributes_set in group_map.items():
        # Find the intersection of user and group attributes
        matching_attributes = user_attributes_set & group_attributes_set
        match_count = len(matching_attributes)

        # Check if this group has the most matches and meets the threshold
        if match_count > max_matching_attributes and match_count >= minimum_matching_threshold:
            max_matching_attributes = match_count
            best_group = group_id

    # Assign the user to the best matching group
    if not best_group:
     new_group = Group(attributes=attributes)
     db.session.add(new_group)
     db.session.commit()

    # Synchronize the new group with the group_map
     group_map[new_group.id] = user_attributes_set
     group_id = new_group.id

    else:
        # Create a new group if no group meets the threshold
        new_group = Group(attributes=attributes)
        db.session.add(new_group)
        db.session.commit()

        # Add the new group to the group_map
        group_map[new_group.id] = user_attributes_set
        group_id = new_group.id

    # Update the user's group ID in the database
    user = User.query.get(user_id)
    user.group_id = group_id
    db.session.commit()

    return group_id

