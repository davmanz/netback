// 📂 src/hooks/useClassificationForm.js
import { useState } from "react";

const FIELDS = ["country", "site", "area", "model", "deviceType", "manufacturer"];

export const useClassificationForm = (initialVaultCredential = null) => {
  const [formData, setFormData] = useState({
    name: "",
    vaultCredential: initialVaultCredential,
    rules: FIELDS.reduce((acc, f) => ({ ...acc, [f]: [] }), {}),
  });

  const [newRules, setNewRules] = useState(
    FIELDS.reduce((acc, field) => {
      acc[field] = { value: "", assign: "", searchIn: [] };
      return acc;
    }, {})
  );

  const [errors, setErrors] = useState({});
  const [isDirty, setIsDirty] = useState(false);

  const resetForm = () => {
    setFormData({
      name: "",
      vaultCredential: null,
      rules: FIELDS.reduce((acc, f) => ({ ...acc, [f]: [] }), {}),
    });
    setNewRules(
      FIELDS.reduce((acc, field) => {
        acc[field] = { value: "", assign: "", searchIn: [] };
        return acc;
      }, {})
    );
    setErrors({});
    setIsDirty(false);
  };

  const handleAddRule = (field) => {
    const rule = newRules[field];
    if (!rule.value || !rule.assign || rule.searchIn.length === 0) return;

    setFormData((prev) => ({
      ...prev,
      rules: {
        ...prev.rules,
        [field]: [...prev.rules[field], { ...rule }],
      },
    }));

    setNewRules((prev) => ({
      ...prev,
      [field]: { value: "", assign: "", searchIn: [] },
    }));

    setIsDirty(true);
  };

  const handleCheckboxChange = (field, option) => {
    setNewRules((prev) => {
      const current = prev[field];
      const updated = current.searchIn.includes(option)
        ? current.searchIn.filter((i) => i !== option)
        : [...current.searchIn, option];

      return {
        ...prev,
        [field]: { ...current, searchIn: updated },
      };
    });

    setIsDirty(true);
  };

  const validateForm = () => {
    const newErrors = {};
    if (!formData.name.trim()) newErrors.name = "El nombre es requerido";

    for (const field of FIELDS) {
      if (formData.rules[field].length === 0) {
        newErrors[field] = `Se requiere al menos una regla para ${field}`;
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  return {
    formData,
    setFormData,
    newRules,
    setNewRules,
    errors,
    isDirty,
    resetForm,
    handleAddRule,
    handleCheckboxChange,
    validateForm,
    setIsDirty,
  };
};
