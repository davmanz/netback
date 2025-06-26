import {
  Paper,
  Typography,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Box,
} from "@mui/material";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";

const renderSectionDiff = (sections, label) => (
  sections?.length > 0 ? sections.map((section, i) => {
    const title = Object.keys(section)[0];
    const lines = section[title];
    return (
      <Box key={i} sx={{ mb: 2 }}>
        <Typography variant="subtitle2" sx={{ fontWeight: "bold" }}>
          {title}
        </Typography>
        <pre style={{ margin: 0 }}>
          {lines.map((line, idx) => {
            let color = "inherit";
            if (line.startsWith("++")) color = "green";
            else if (line.startsWith("--")) color = "red";
            return (
              <div key={idx} style={{ color }}>
                {line}
              </div>
            );
          })}
        </pre>
      </Box>
    );
  }) : (
    <Typography>No hay {label}.</Typography>
  )
);

const renderVlanChanges = (vlanInfo) => {
  if (!vlanInfo || !vlanInfo.ports_vlan) return <Typography>No hay cambios en VLANs.</Typography>;

  return Object.entries(vlanInfo.ports_vlan).map(([vlan, changes], i) => (
    <Box key={i} sx={{ mb: 2 }}>
      <Typography variant="subtitle2">VLAN {vlan}</Typography>
      <Typography variant="body2" color="green">
        Asignados: {changes.assigned?.join(", ") || "Ninguno"}
      </Typography>
      <Typography variant="body2" color="red">
        Removidos: {changes.removed?.join(", ") || "Ninguno"}
      </Typography>
    </Box>
  ));
};

const ComparisonResult = ({ comparisonResult }) => {
  if (!comparisonResult) return null;

  return (
    <Paper sx={{ mt: 4, padding: 2 }}>
      <Typography variant="h5">Resultado de la Comparación</Typography>

      <Accordion defaultExpanded>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography>🔹 Configuraciones Agregadas</Typography>
        </AccordionSummary>
        <AccordionDetails>
          {renderSectionDiff(comparisonResult.added, "configuraciones agregadas")}
        </AccordionDetails>
      </Accordion>

      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography>🔸 Configuraciones Eliminadas</Typography>
        </AccordionSummary>
        <AccordionDetails>
          {renderSectionDiff(comparisonResult.removed, "configuraciones eliminadas")}
        </AccordionDetails>
      </Accordion>

      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography>🔧 Configuraciones Modificadas</Typography>
        </AccordionSummary>
        <AccordionDetails>
          {renderSectionDiff(comparisonResult.modified, "configuraciones modificadas")}
        </AccordionDetails>
      </Accordion>

      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography>🟢 Cambios en VLANs</Typography>
        </AccordionSummary>
        <AccordionDetails>
          {renderVlanChanges(comparisonResult.vlanInfo)}
        </AccordionDetails>
      </Accordion>
    </Paper>
  );
};

export default ComparisonResult;
