"""
Model registry for managing trained models.

Handles model versioning, loading, and lifecycle management.
"""
import logging
import json
from datetime import date, datetime
from pathlib import Path
from typing import Any

from app.ml.models.ensemble import EnsemblePredictor
from app.ml.models.predictor import StatPredictor
from app.ml.models.base import ModelMetadata

logger = logging.getLogger(__name__)


class ModelRegistry:
    """
    Registry for managing ML models.

    Handles model versioning, storage, and retrieval.
    """

    # Default paths
    DEFAULT_MODEL_DIR = Path("models")
    REGISTRY_FILE = "registry.json"

    def __init__(self, model_dir: str | None = None):
        """
        Initialize model registry.

        Args:
            model_dir: Directory for model storage.
        """
        self.model_dir = Path(model_dir) if model_dir else self.DEFAULT_MODEL_DIR
        self.model_dir.mkdir(parents=True, exist_ok=True)

        self.registry_path = self.model_dir / self.REGISTRY_FILE
        self._registry: dict[str, dict] = self._load_registry()
        self.logger = logging.getLogger(__name__)

    def register_model(
        self,
        model: EnsemblePredictor | StatPredictor,
        model_name: str,
        version: str | None = None,
        tags: list[str] | None = None
    ) -> str:
        """
        Register and save a trained model.

        Args:
            model: Trained model instance.
            model_name: Name for the model.
            version: Version string (auto-generated if not provided).
            tags: Optional tags for the model.

        Returns:
            Model ID in registry.
        """
        version = version or self._generate_version()
        model_id = f"{model_name}_{version}"

        # Save model file
        model_path = self.model_dir / f"{model_id}.pkl"
        model.save(str(model_path))

        # Get metadata
        metadata = {}
        if hasattr(model, 'metadata') and model.metadata:
            metadata = model.metadata.to_dict()

        # Register in registry
        self._registry[model_id] = {
            "model_name": model_name,
            "version": version,
            "path": str(model_path),
            "registered_at": datetime.utcnow().isoformat(),
            "stat_type": model.stat_type,
            "tags": tags or [],
            "metadata": metadata,
            "is_active": True,
        }

        self._save_registry()

        self.logger.info(f"Registered model: {model_id}")

        return model_id

    def load_model(
        self,
        model_name: str,
        version: str | None = None
    ) -> EnsemblePredictor | StatPredictor | None:
        """
        Load a model from registry.

        Args:
            model_name: Name of the model.
            version: Specific version (latest if not provided).

        Returns:
            Loaded model or None if not found.
        """
        # Find model in registry
        if version:
            model_id = f"{model_name}_{version}"
            if model_id not in self._registry:
                self.logger.error(f"Model {model_id} not found")
                return None
        else:
            # Get latest version
            model_id = self._get_latest_version(model_name)
            if not model_id:
                self.logger.error(f"No models found for {model_name}")
                return None

        entry = self._registry[model_id]
        model_path = entry["path"]

        if not Path(model_path).exists():
            self.logger.error(f"Model file not found: {model_path}")
            return None

        # Determine model type and load
        stat_type = entry.get("stat_type", "fantasy_points")

        try:
            # Try loading as ensemble first
            model = EnsemblePredictor(stat_type=stat_type)
            model.load(model_path)
            return model
        except Exception:
            try:
                # Fall back to single model
                model = StatPredictor(stat_type=stat_type)
                model.load(model_path)
                return model
            except Exception as e:
                self.logger.error(f"Failed to load model: {e}")
                return None

    def get_active_model(self, stat_type: str) -> str | None:
        """
        Get the active model ID for a stat type.

        Args:
            stat_type: Stat type to get model for.

        Returns:
            Model ID or None.
        """
        for model_id, entry in self._registry.items():
            if entry.get("stat_type") == stat_type and entry.get("is_active"):
                return model_id

        # Fall back to latest
        return self._get_latest_by_stat_type(stat_type)

    def set_active_model(self, model_id: str) -> bool:
        """
        Set a model as the active model for its stat type.

        Args:
            model_id: Model ID to activate.

        Returns:
            Success status.
        """
        if model_id not in self._registry:
            return False

        stat_type = self._registry[model_id].get("stat_type")

        # Deactivate other models of same stat type
        for mid, entry in self._registry.items():
            if entry.get("stat_type") == stat_type:
                entry["is_active"] = (mid == model_id)

        self._save_registry()

        return True

    def list_models(
        self,
        stat_type: str | None = None,
        tags: list[str] | None = None
    ) -> list[dict[str, Any]]:
        """
        List registered models.

        Args:
            stat_type: Filter by stat type.
            tags: Filter by tags.

        Returns:
            List of model entries.
        """
        results = []

        for model_id, entry in self._registry.items():
            # Apply filters
            if stat_type and entry.get("stat_type") != stat_type:
                continue

            if tags:
                model_tags = set(entry.get("tags", []))
                if not set(tags).issubset(model_tags):
                    continue

            results.append({
                "model_id": model_id,
                **entry
            })

        # Sort by registration date
        results.sort(key=lambda x: x.get("registered_at", ""), reverse=True)

        return results

    def delete_model(self, model_id: str, delete_file: bool = True) -> bool:
        """
        Delete a model from registry.

        Args:
            model_id: Model ID to delete.
            delete_file: Also delete the model file.

        Returns:
            Success status.
        """
        if model_id not in self._registry:
            return False

        entry = self._registry[model_id]

        # Delete file if requested
        if delete_file:
            model_path = Path(entry["path"])
            if model_path.exists():
                model_path.unlink()

        # Remove from registry
        del self._registry[model_id]
        self._save_registry()

        self.logger.info(f"Deleted model: {model_id}")

        return True

    def get_model_metrics(self, model_id: str) -> dict[str, Any] | None:
        """
        Get metrics for a registered model.

        Args:
            model_id: Model ID.

        Returns:
            Metrics dictionary or None.
        """
        if model_id not in self._registry:
            return None

        entry = self._registry[model_id]
        return entry.get("metadata", {}).get("metrics", {})

    def compare_models(
        self,
        model_ids: list[str]
    ) -> list[dict[str, Any]]:
        """
        Compare metrics across models.

        Args:
            model_ids: List of model IDs to compare.

        Returns:
            Comparison data.
        """
        comparisons = []

        for model_id in model_ids:
            if model_id not in self._registry:
                continue

            entry = self._registry[model_id]
            metrics = entry.get("metadata", {}).get("metrics", {})

            comparisons.append({
                "model_id": model_id,
                "version": entry.get("version"),
                "stat_type": entry.get("stat_type"),
                "is_active": entry.get("is_active"),
                "registered_at": entry.get("registered_at"),
                **metrics
            })

        return comparisons

    def _load_registry(self) -> dict[str, dict]:
        """Load registry from disk."""
        if not self.registry_path.exists():
            return {}

        try:
            with open(self.registry_path, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load registry: {e}")
            return {}

    def _save_registry(self) -> None:
        """Save registry to disk."""
        try:
            with open(self.registry_path, "w") as f:
                json.dump(self._registry, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save registry: {e}")

    def _generate_version(self) -> str:
        """Generate version string based on date."""
        return datetime.utcnow().strftime("%Y%m%d_%H%M%S")

    def _get_latest_version(self, model_name: str) -> str | None:
        """Get latest version of a model."""
        matching = [
            (mid, entry) for mid, entry in self._registry.items()
            if entry.get("model_name") == model_name
        ]

        if not matching:
            return None

        # Sort by registration date
        matching.sort(key=lambda x: x[1].get("registered_at", ""), reverse=True)

        return matching[0][0]

    def _get_latest_by_stat_type(self, stat_type: str) -> str | None:
        """Get latest model for a stat type."""
        matching = [
            (mid, entry) for mid, entry in self._registry.items()
            if entry.get("stat_type") == stat_type
        ]

        if not matching:
            return None

        matching.sort(key=lambda x: x[1].get("registered_at", ""), reverse=True)

        return matching[0][0]
