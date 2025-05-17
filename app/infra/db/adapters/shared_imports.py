import os
import itertools
import pymongo
import re
from dotenv import load_dotenv
from pymongo import MongoClient
from bson import ObjectId
from bson.errors import InvalidId
from app.infra.log_service import logger
from app.shared.exceptions import (
    URIConnectionError, InvalidIdError, DocNotFoundError, DocsNotFoundError,
    EmptySearchError, ExistingSubscriptionError, DuplicateEntityError
)
from app.shared.serializer import Serializer
from pymongo.errors import DuplicateKeyError, BulkWriteError
from pymongo.results import InsertOneResult
from pymongo.cursor import Cursor
from pymongo import UpdateOne, ReplaceOne
from typing import Generator, Any, List, Dict, Mapping