<template>
  <DailyBarChart v-bind="$attrs" />
</template>

<script>
import DailyBarChart from './DailyBarChart.vue';

export default {
  name: 'DailyBarAnalytics',
  components: {
    DailyBarChart
  }
};
</script>
