from dataclasses import dataclass
import logging
import sqlite3
from typing import Any

#Continue: Need to add db connection stuff

logger = logging.getLogger(__name__)
configure_logger(logger)

#Question: Do I need a class here (i.e. class Meal)? 

# Modeled after create_meal function in kitchen_model
def create_study_session(studysession_json: str) -> None:
    """
    Creates a new study session in the database

    Args:
        studysession_json (str): JSON string of studysession_list
    
    Raises:
        ValueError: Database Error
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO studysessions (studysession_json)
                VALUES (?)
            """, (studysession_json))
            conn.commit()

            logger.info("Study Session successfully added to the database")
    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e
    
# Question: There is no clear_meals() function for clear_catalog function in app.py?

# Modeled after delete_meal function in kitchen_model
def delete_study_session(study_session_id: int) -> None:
    """
        Deletes a meal from the database.

        Args:
            meal_id (int): The ID of the meal to remove from the database.

        Raises:
            ValueError: If the meal with the meal_id is not found.
    """

    '''
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT deleted FROM meals WHERE id = ?", (meal_id,))
            try:
                deleted = cursor.fetchone()[0]
                if deleted:
                    logger.info("Meal with ID %s has already been deleted", meal_id)
                    raise ValueError(f"Meal with ID {meal_id} has been deleted")
            except TypeError:
                logger.info("Meal with ID %s not found", meal_id)
                raise ValueError(f"Meal with ID {meal_id} not found")

            cursor.execute("UPDATE meals SET deleted = TRUE WHERE id = ?", (meal_id,))
            conn.commit()

            logger.info("Meal with ID %s marked as deleted.", meal_id)

    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e
    '''
