import { useState } from "react";
import {
  Box, TextField, FormControl, Select, MenuItem, InputLabel, Typography, Paper,
  IconButton, Button, Grid, Tooltip, List, ListItem, ListItemText, ListItemSecondaryAction,
 FormControlLabel, Checkbox
} from "@mui/material";
import DeleteIcon from "@mui/icons-material/Delete";
import AddIcon from "@mui/icons-material/Add";
import EditIcon from "@mui/icons-material/Edit";

// Campos de clasificación disponibles
const CLASSIFICATION_FIELDS = [
  "manufacturer", "deviceType", "model", "country", "site", "area"
];

// Campos donde buscar disponibles
const SEARCH_IN_OPTIONS = ["hostname", "tags", "groups"];

export const EditRuleSetForm = ({ ruleSet, vaultCredentials, onSubmit }) => {
  const [name, setName] = useState(ruleSet.name);
  const [vaultCredential, setVaultCredential] = useState(ruleSet.vaultCredential || "");
  const [rules, setRules] = useState(ruleSet.rules || {});
  
  // Estado para el formulario de nueva regla
  const [editingField, setEditingField] = useState("");
  const [editingRule, setEditingRule] = useState(null);
  const [showNewRuleForm, setShowNewRuleForm] = useState(false);
  const [newRule, setNewRule] = useState({
    value: "",
    assign: "",
    searchIn: []
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({
      name,
      vaultCredential,
      rules
    });
  };

  const handleAddRule = () => {
    if (!editingField || !newRule.value || !newRule.assign || newRule.searchIn.length === 0) {
      return; // Validación básica
    }

    const updatedRules = { ...rules };
    
    // Si el campo no existe, lo inicializamos
    if (!updatedRules[editingField]) {
      updatedRules[editingField] = [];
    }
    
    if (editingRule !== null) {
      // Estamos editando una regla existente
      updatedRules[editingField][editingRule] = { ...newRule };
    } else {
      // Añadimos una nueva regla
      updatedRules[editingField].push({ ...newRule });
    }
    
    setRules(updatedRules);
    resetRuleForm();
  };

  const handleDeleteRule = (field, index) => {
    const updatedRules = { ...rules };
    updatedRules[field].splice(index, 1);
    
    // Si no quedan reglas para este campo, eliminamos el campo
    if (updatedRules[field].length === 0) {
      delete updatedRules[field];
    }
    
    setRules(updatedRules);
  };

  const handleEditRule = (field, index) => {
    setEditingField(field);
    setEditingRule(index);
    setNewRule({ ...rules[field][index] });
    setShowNewRuleForm(true);
  };

  const resetRuleForm = () => {
    setShowNewRuleForm(false);
    setEditingField("");
    setEditingRule(null);
    setNewRule({
      value: "",
      assign: "",
      searchIn: []
    });
  };

  const handleSearchInToggle = (option) => {
    const currentSearchIn = [...newRule.searchIn];
    const index = currentSearchIn.indexOf(option);
    
    if (index === -1) {
      currentSearchIn.push(option);
    } else {
      currentSearchIn.splice(index, 1);
    }
    
    setNewRule({ ...newRule, searchIn: currentSearchIn });
  };

  return (
    <Box
      component="form"
      id="edit-rule-form"
      onSubmit={handleSubmit}
      sx={{ display: "flex", flexDirection: "column", gap: 2 }}
    >
      <Paper sx={{ p: 2 }}>
        <Typography variant="subtitle1" gutterBottom>🔧 Información General</Typography>

        <TextField
          fullWidth
          label="Nombre del conjunto"
          value={name}
          onChange={(e) => setName(e.target.value)}
          margin="normal"
        />

        <FormControl fullWidth sx={{ mt: 2 }}>
          <InputLabel>Credencial Vault</InputLabel>
          <Select
            value={vaultCredential}
            onChange={(e) => setVaultCredential(e.target.value)}
          >
            <MenuItem value="">-- Ninguna --</MenuItem>
            {vaultCredentials.map((cred) => (
              <MenuItem key={cred.id} value={cred.id}>{cred.nick}</MenuItem>
            ))}
          </Select>
        </FormControl>
      </Paper>

      <Paper sx={{ p: 2 }}>
        <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 2 }}>
          <Typography variant="subtitle1">📋 Reglas de Clasificación</Typography>
          <Button 
            startIcon={<AddIcon />} 
            variant="outlined" 
            color="primary"
            onClick={() => setShowNewRuleForm(true)}
            disabled={showNewRuleForm}
          >
            Añadir Regla
          </Button>
        </Box>

        {showNewRuleForm && (
          <Paper variant="outlined" sx={{ p: 2, mb: 3 }}>
            <Typography variant="subtitle2" gutterBottom>
              {editingRule !== null ? 'Editar regla' : 'Nueva regla de clasificación'}
            </Typography>
            
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth margin="dense">
                  <InputLabel>Campo a clasificar</InputLabel>
                  <Select
                    value={editingField}
                    onChange={(e) => setEditingField(e.target.value)}
                    disabled={editingRule !== null}
                  >
                    {CLASSIFICATION_FIELDS.map((field) => (
                      <MenuItem key={field} value={field}>
                        {field.charAt(0).toUpperCase() + field.slice(1)}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Valor a buscar"
                  value={newRule.value}
                  onChange={(e) => setNewRule({ ...newRule, value: e.target.value })}
                  margin="dense"
                />
              </Grid>
              
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Valor a asignar"
                  value={newRule.assign}
                  onChange={(e) => setNewRule({ ...newRule, assign: e.target.value })}
                  margin="dense"
                />
              </Grid>
              
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" gutterBottom>Buscar en:</Typography>
                {SEARCH_IN_OPTIONS.map((option) => (
                  <FormControlLabel
                    key={option}
                    control={
                      <Checkbox
                        checked={newRule.searchIn.includes(option)}
                        onChange={() => handleSearchInToggle(option)}
                      />
                    }
                    label={option}
                  />
                ))}
              </Grid>
              
              <Grid item xs={12}>
                <Box sx={{ display: "flex", justifyContent: "flex-end", gap: 1, mt: 1 }}>
                  <Button onClick={resetRuleForm} color="inherit">
                    Cancelar
                  </Button>
                  <Button
                    variant="contained"
                    onClick={handleAddRule}
                    disabled={
                      !editingField || 
                      !newRule.value || 
                      !newRule.assign || 
                      newRule.searchIn.length === 0
                    }
                  >
                    {editingRule !== null ? 'Guardar cambios' : 'Añadir regla'}
                  </Button>
                </Box>
              </Grid>
            </Grid>
          </Paper>
        )}

        {/* Lista de reglas existentes */}
        {Object.keys(rules).length === 0 ? (
          <Typography variant="body2" color="text.secondary" align="center" sx={{ py: 3 }}>
            No hay reglas configuradas. Añade una regla nueva para comenzar.
          </Typography>
        ) : (
          Object.keys(rules).map((field) => (
            <Box key={field} sx={{ mb: 2 }}>
              <Typography variant="subtitle2" sx={{ mt: 2, mb: 1 }}>
                {field.charAt(0).toUpperCase() + field.slice(1)}
              </Typography>
              <List dense sx={{ bgcolor: 'background.paper' }}>
                {rules[field].map((rule, index) => (
                  <ListItem key={index} divider={index < rules[field].length - 1}>
                    <ListItemText
                      primary={`${rule.value} → ${rule.assign}`}
                      secondary={`Buscar en: ${rule.searchIn.join(', ')}`}
                    />
                    <ListItemSecondaryAction>
                      <Tooltip title="Editar">
                        <IconButton edge="end" onClick={() => handleEditRule(field, index)}>
                          <EditIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Eliminar">
                        <IconButton edge="end" onClick={() => handleDeleteRule(field, index)}>
                          <DeleteIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </ListItemSecondaryAction>
                  </ListItem>
                ))}
              </List>
            </Box>
          ))
        )}
      </Paper>
    </Box>
  );
};

export default EditRuleSetForm;