import { Stepper, Step, StepLabel, Button, Box, Tooltip } from "@mui/material";
import {
  ArrowBack as ArrowBackIcon,
  ArrowForward as ArrowForwardIcon,
  Save as SaveIcon,
} from "@mui/icons-material";

const StepperNavigation = ({ step, setStep, steps, onSubmit, loading }) => {
  const isLastStep = step === steps.length - 1;

  return (
    <Box sx={{ flex: 1 }}>
      <Stepper activeStep={step} alternativeLabel>
        {steps.map((s) => (
          <Step key={s.label}>
            <StepLabel>{s.label}</StepLabel>
          </Step>
        ))}
      </Stepper>

      <Box
        sx={{
          mt: 4,
          display: "flex",
          justifyContent: "space-between",
          width: "100%",
          maxWidth: 500,
          margin: "20px auto",
          px: 2,
        }}
      >
        <Tooltip title="Volver al paso anterior">
          <span>
            <Button
              variant="outlined"
              onClick={() => setStep((prev) => Math.max(prev - 1, 0))}
              disabled={step === 0}
              startIcon={<ArrowBackIcon />}
              aria-label="Volver al paso anterior"
            >
              Atrás
            </Button>
          </span>
        </Tooltip>

        {isLastStep ? (
          <Tooltip title="Guardar configuración">
            <span>
              <Button
                variant="contained"
                color="success"
                onClick={onSubmit}
                disabled={loading}
                endIcon={<SaveIcon />}
                aria-label="Guardar configuración"
              >
                {loading ? "Guardando..." : "Guardar"}
              </Button>
            </span>
          </Tooltip>
        ) : (
          <Tooltip title="Ir al siguiente paso">
            <span>
              <Button
                variant="contained"
                color="primary"
                onClick={() => setStep((prev) => prev + 1)}
                endIcon={<ArrowForwardIcon />}
                aria-label="Ir al siguiente paso"
              >
                Siguiente
              </Button>
            </span>
          </Tooltip>
        )}
      </Box>
    </Box>
  );
};

export default StepperNavigation;
