import { useEffect, useState } from "react";
import {
  Dialog, DialogTitle, DialogContent, DialogActions,
  Button, Alert
} from "@mui/material";
import {
  getClassificationRules,
  getVaultCredentials,
  getCountries,
  getSites,
  getAreas,
  getManufacturers,
  getDeviceTypes,
  saveClassificationRuleSet
} from "../../api";
import { useClassificationForm } from "../../hooks/useClassificationForm";
import RuleSetEditor from "./RuleSetEditor";

const FIELDS = ["country", "site", "area", "model", "deviceType", "manufacturer"];

export const RuleSetModal = ({ open, onClose, ruleSetId, onSaved }) => {
  const [initData, setInitData] = useState({
  vaultCredentials: [],
  assignOptions: {},
});

  const [loading, setLoading] = useState(true);

  const {
    formData, setFormData, newRules, setNewRules,
    errors, resetForm,
    handleAddRule, handleCheckboxChange, validateForm, setIsDirty
  } = useClassificationForm();

  useEffect(() => {
    const fetchData = async () => {
      const [rules, creds, countries, sites, areas, manufacturers, deviceTypes] =
        await Promise.all([
          getClassificationRules(),
          getVaultCredentials(),
          getCountries(),
          getSites(),
          getAreas(),
          getManufacturers(),
          getDeviceTypes()
        ]);

      setInitData({
        vaultCredentials: creds,
        assignOptions: {
          country: [...new Set(countries.map((c) => c.name))],
          site: [...new Set(sites.map((s) => s.name))],
          area: [...new Set(areas.map((a) => a.name))],
          manufacturer: [...new Set(manufacturers.map((m) => m.name))],
          deviceType: [...new Set(deviceTypes.map((d) => d.name))],
        }
      });


      const selected = rules.find((r) => r.id === ruleSetId);
      if (selected) {
        setFormData({
          name: selected.name,
          vaultCredential: selected.vaultCredential || null,
          rules: selected.rules,
        });
        setIsDirty(false);
      } else {
        resetForm();
      }

      setLoading(false);
    };

    if (open) {
      fetchData();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open, ruleSetId,]);

  const handleSave = async () => {
    if (!validateForm()) return;

    const payload = {
      name: formData.name,
      vaultCredential: formData.vaultCredential,
      rules: formData.rules,
    };

    const res = await saveClassificationRuleSet(ruleSetId, payload);
    if (res?.id) {
      onSaved?.();
      resetForm();
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>{ruleSetId ? "Editar Conjunto de Reglas" : "Nuevo Conjunto de Reglas"}</DialogTitle>
      <DialogContent>
        {loading ? (
          <Alert severity="info">Cargando datos...</Alert>
        ) : (
          <RuleSetEditor
            formData={formData}
            setFormData={setFormData}
            newRules={newRules}
            setNewRules={setNewRules}
            assignOptions={initData.assignOptions}
            errors={errors}
            handleAddRule={handleAddRule}
            handleCheckboxChange={handleCheckboxChange}
            vaultCredentials={initData.vaultCredentials}
            ruleFields={FIELDS}
            isEdit={!!ruleSetId}
          />
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancelar</Button>
        <Button variant="contained" onClick={handleSave}>Guardar</Button>
      </DialogActions>
    </Dialog>
  );
};

export default RuleSetModal;
