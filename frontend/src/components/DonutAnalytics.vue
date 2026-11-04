<template>
  <DonutChart v-bind="$attrs" />
</template>

<script>
import DonutChart from './DonutChart.vue';

export default {
  name: 'DonutAnalytics',
  components: {
    DonutChart
  }
};
</script>
