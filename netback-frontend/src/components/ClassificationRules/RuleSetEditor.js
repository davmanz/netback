import {
  Box, TextField, Select, MenuItem, InputLabel, FormControl, FormGroup,
  FormControlLabel, Checkbox, Button, Typography, Paper,
  Tooltip, Breadcrumbs, Link, useTheme
} from "@mui/material";

const RuleSetEditor = ({
  formData, setFormData, newRules, setNewRules, assignOptions, errors,
  handleAddRule, handleCheckboxChange, vaultCredentials,
  ruleFields, isEdit
  }) => {
    const theme = useTheme();

    const handleInputChange = (e) => {
      setFormData((prev) => ({
        ...prev,
        [e.target.name]: e.target.value
      }));
    };

    return (
      <Box component={Paper} sx={{ p: 3 }}>
        <Breadcrumbs sx={{ mb: 2 }}>
          <Link color="inherit" href="/classification-rules">
            Reglas
          </Link>
          <Typography color="textPrimary">
            {isEdit ? "Editar Conjunto" : "Nuevo Conjunto"}
          </Typography>
        </Breadcrumbs>

        <Typography variant="h6" gutterBottom>
          {isEdit ? "✏️ Editar Conjunto de Reglas" : "➕ Nuevo Conjunto"}
        </Typography>

        <TextField
          fullWidth
          label="Nombre del conjunto"
          name="name"
          value={formData.name}
          onChange={handleInputChange}
          error={!!errors.name}
          helperText={errors.name}
          sx={{ mb: 2 }}
        />

        <Tooltip title="Seleccione una credencial para acceder a recursos protegidos">
          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>Credencial Vault (opcional)</InputLabel>
            <Select
              name="vaultCredential"
              value={formData.vaultCredential || ""}
              onChange={handleInputChange}
            >
              <MenuItem value="">-- Ninguna --</MenuItem>
              {vaultCredentials.map((cred) => (
                <MenuItem key={cred.id} value={cred.id}>{cred.nick}</MenuItem>
              ))}
            </Select>
          </FormControl>
        </Tooltip>

        <Typography variant="subtitle1">Reglas de Clasificación:</Typography>

        {ruleFields.map((field) => (
          <Paper
            key={field}
            elevation={2}
            sx={{
              p: 2,
              mb: 2,
              backgroundColor: theme.palette.mode === "dark" ? "#1e1e1e" : "#fafafa",
              border: `1px solid ${theme.palette.divider}`,
              borderRadius: 2,
              '&:hover': {
                backgroundColor: theme.palette.mode === "dark" ? "#2a2a2a" : "#f5f5f5",
                boxShadow: 3
              }
            }}
          >
            <Typography variant="body2" sx={{ mb: 1 }}>🔸 {field.toUpperCase()}</Typography>

            {/* value es campo libre */}
            <TextField
              fullWidth
              label="Patrón a detectar (value)"
              value={newRules[field]?.value || ""}
              onChange={(e) =>
                setNewRules((prev) => ({
                  ...prev,
                  [field]: { ...prev[field], value: e.target.value }
                }))
              }
              sx={{ mb: 1 }}
            />

            {/* assign sí es selección */}
            <FormControl fullWidth sx={{ mb: 1 }}>
              <InputLabel>Asignar a</InputLabel>
              <Select
                value={newRules[field]?.assign || ""}
                onChange={(e) =>
                  setNewRules((prev) => ({
                    ...prev,
                    [field]: { ...prev[field], assign: e.target.value }
                  }))
                }
              >
                <MenuItem value="">-- Ninguno --</MenuItem>
                {(assignOptions[field] || []).map((option, i) => (
                  <MenuItem key={i} value={option}>{option}</MenuItem>
                ))}
              </Select>
            </FormControl>

            {/* Checkboxes para searchIn */}
            <FormGroup
              row
              sx={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
                gap: 1
              }}
            >
              {["hostname", "tags", "groups"].map((option) => (
                <FormControlLabel
                  key={option}
                  control={
                    <Checkbox
                      checked={newRules[field]?.searchIn?.includes(option)}
                      onChange={() => handleCheckboxChange(field, option)}
                    />
                  }
                  label={option}
                />
              ))}
            </FormGroup>

            <Button
              variant="outlined"
              size="small"
              onClick={() => handleAddRule(field)}
              sx={{ mt: 1 }}
            >
              ➕ Agregar Regla para {field}
            </Button>
          </Paper>
        ))}
      </Box>
    );
};

export default RuleSetEditor;
