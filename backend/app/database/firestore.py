import time
from typing import Dict, List, Optional, Any
from app.core.firebase import get_firestore_client
from app.core.logging import logger

# In-memory storage fallback for local execution when Firebase is unconfigured
_in_memory_db: Dict[str, Dict[str, Any]] = {
    "users": {},
    "analyses": {},
    "chat_sessions": {},
    "messages": {},
    "uploaded_files": {},
    "activity_logs": {},
    "settings": {}
}

import json
import numpy as np

def sanitize_for_firestore(obj: Any) -> Any:
    """Recursively converts nested dictionaries and complex arrays into valid Firestore formats."""
    if isinstance(obj, dict):
        return {str(k): sanitize_for_firestore(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple, set)):
        sanitized_list = []
        for item in obj:
            if isinstance(item, (list, tuple, set)):
                sanitized_list.append(json.dumps([sanitize_for_firestore(sub) for sub in item]))
            else:
                sanitized_list.append(sanitize_for_firestore(item))
        return sanitized_list
    elif isinstance(obj, (np.floating, float)):
        return float(obj)
    elif isinstance(obj, (np.integer, int)):
        return int(obj)
    elif isinstance(obj, (np.bool_, bool)):
        return bool(obj)
    elif isinstance(obj, (int, float, str, bool)) or obj is None:
        return obj
    elif hasattr(obj, "model_dump"):
        return sanitize_for_firestore(obj.model_dump())
    elif hasattr(obj, "to_dict"):
        return sanitize_for_firestore(obj.to_dict())
    else:
        return str(obj)

class FirestoreRepository:
    def __init__(self):
        self.db = get_firestore_client()

    def set_document(self, collection_name: str, doc_id: str, data: dict) -> dict:
        data["updated_at"] = int(time.time())
        if "created_at" not in data:
            data["created_at"] = int(time.time())

        # Sync to in-memory store
        if collection_name not in _in_memory_db:
            _in_memory_db[collection_name] = {}
        _in_memory_db[collection_name][doc_id] = data

        if self.db:
            try:
                clean_data = sanitize_for_firestore(data)
                self.db.collection(collection_name).document(doc_id).set(clean_data, merge=True)
                return data
            except Exception as e:
                logger.error(f"Firestore set_document error ({collection_name}/{doc_id}): {e}")

        return data

    def get_document(self, collection_name: str, doc_id: str) -> Optional[dict]:
        if self.db:
            try:
                doc = self.db.collection(collection_name).document(doc_id).get()
                if doc.exists:
                    return doc.to_dict()
            except Exception as e:
                logger.error(f"Firestore get_document error ({collection_name}/{doc_id}): {e}")

        # Fallback in-memory
        return _in_memory_db.get(collection_name, {}).get(doc_id)

    def query_collection(self, collection_name: str, field: Optional[str] = None, op: Optional[str] = "==", value: Optional[Any] = None, limit: int = 50) -> List[dict]:
        combined_dict = {}
        
        # 1. Read from in-memory cache
        coll = _in_memory_db.get(collection_name, {})
        for doc_id, doc in coll.items():
            if field and value is not None:
                if op == "==" and doc.get(field) == value:
                    combined_dict[doc_id] = doc
            else:
                combined_dict[doc_id] = doc

        # 2. Read from Firestore
        if self.db:
            try:
                ref = self.db.collection(collection_name)
                if field and value is not None:
                    ref = ref.where(field, op, value)
                docs = ref.limit(limit).stream()
                for doc in docs:
                    d_data = doc.to_dict()
                    d_id = doc.id
                    combined_dict[d_id] = d_data
            except Exception as e:
                logger.error(f"Firestore query error ({collection_name}): {e}")

        results = list(combined_dict.values())
        return results[:limit]

    def delete_document(self, collection_name: str, doc_id: str) -> bool:
        if self.db:
            try:
                self.db.collection(collection_name).document(doc_id).delete()
                return True
            except Exception as e:
                logger.error(f"Firestore delete error ({collection_name}/{doc_id}): {e}")

        if collection_name in _in_memory_db and doc_id in _in_memory_db[collection_name]:
            del _in_memory_db[collection_name][doc_id]
            return True
        return False

db_repo = FirestoreRepository()