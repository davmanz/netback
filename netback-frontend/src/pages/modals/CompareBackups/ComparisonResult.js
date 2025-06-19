import {
  Paper,
  Typography,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from "@mui/material";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";

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
          {comparisonResult.added?.length > 0 ? (
            <pre>{JSON.stringify(comparisonResult.added, null, 2)}</pre>
          ) : (
            <Typography>No hay configuraciones agregadas.</Typography>
          )}
        </AccordionDetails>
      </Accordion>

      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography>🔸 Configuraciones Eliminadas</Typography>
        </AccordionSummary>
        <AccordionDetails>
          {comparisonResult.removed?.length > 0 ? (
            <pre>{JSON.stringify(comparisonResult.removed, null, 2)}</pre>
          ) : (
            <Typography>No hay configuraciones eliminadas.</Typography>
          )}
        </AccordionDetails>
      </Accordion>

      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography>🟢 Cambios en VLANs</Typography>
        </AccordionSummary>
        <AccordionDetails>
          {comparisonResult.vlanInfo && Object.keys(comparisonResult.vlanInfo).length > 0 ? (
            <pre>{JSON.stringify(comparisonResult.vlanInfo, null, 2)}</pre>
          ) : (
            <Typography>No hay cambios en VLANs.</Typography>
          )}
        </AccordionDetails>
      </Accordion>
    </Paper>
  );
};

export default ComparisonResult;
