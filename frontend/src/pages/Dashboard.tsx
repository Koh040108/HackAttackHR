import { Grid, Paper, Typography, Box } from '@mui/material';
import {
  People as PeopleIcon,
  Work as WorkIcon,
  Assignment as AssignmentIcon,
  TrendingUp as TrendingUpIcon,
} from '@mui/icons-material';
import { useTheme } from '@mui/material';

const StatCard = ({ title, value, icon }: { title: string; value: string; icon: React.ReactNode }) => (
  <Paper
    sx={{
      p: 3,
      display: 'flex',
      flexDirection: 'column',
      height: 140,
      bgcolor: 'background.paper',
      borderRadius: 2,
      boxShadow: 2,
    }}
  >
    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
      <Typography color="text.secondary" variant="h6">
        {title}
      </Typography>
      {icon}
    </Box>
    <Typography component="p" variant="h4">
      {value}
    </Typography>
  </Paper>
);

const ChartCard = ({ title }: { title: string }) => {
  const theme = useTheme();
  return (
    <Paper
      sx={{
        p: 3,
        display: 'flex',
        flexDirection: 'column',
        bgcolor: theme.palette.background.paper,
        borderRadius: 2,
        boxShadow: 2,
      }}
    >
      <Typography variant="h6" gutterBottom sx={{ color: theme.palette.text.primary }}>
        {title}
      </Typography>
      <Box sx={{ flexGrow: 1, display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
        <Typography variant="body2" sx={{ color: theme.palette.text.secondary }}>Placeholder Chart</Typography>
      </Box>
    </Paper>
  );
};

export default function Dashboard() {
  const theme = useTheme();
  return (
    <Box sx={{ flexGrow: 1 }}>
      <Typography variant="h4" sx={{ mb: 4, color: theme.palette.text.primary }}>
        DASHBOARD
      </Typography>
      <Grid container spacing={3}>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            title="Jobs Posted"
            value="8"
            icon={<WorkIcon sx={{ fontSize: 40, color: theme.palette.primary.main }} />}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            title="Hires Mode"
            value="8"
            icon={<PeopleIcon sx={{ fontSize: 40, color: theme.palette.primary.main }} />}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            title="Total Applicants"
            value="8"
            icon={<AssignmentIcon sx={{ fontSize: 40, color: theme.palette.primary.main }} />}
          />
        </Grid>
        <Grid item xs={12} md={8}>
          <ChartCard title="APPLICATION DISTRIBUTION" />
        </Grid>
        <Grid item xs={12} md={4}>
          <ChartCard title="GENDER DISTRIBUTION" />
        </Grid>
        <Grid item xs={12} md={4}>
          <ChartCard title="RACE DISTRIBUTION" />
        </Grid>
      </Grid>
    </Box>
  );
} 