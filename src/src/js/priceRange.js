export function priceRange() {
  return {
    min: 0,
    max: 35000,
    priceGap: 1000,
    minPercent: 0,
    maxPercent: 35, // initial based on 35000 / 100000 * 100

    formatNumber(num) {
      return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    },

    updateMin() {
      if (this.max - this.min < this.priceGap) {
        this.min = this.max - this.priceGap;
      }
      this.updatePercent();
    },

    updateMax() {
      if (this.max - this.min < this.priceGap) {
        this.max = this.min + this.priceGap;
      }
      this.updatePercent();
    },

    updatePercent() {
      this.minPercent = (this.min / 100000) * 100;
      this.maxPercent = (this.max / 100000) * 100;
    },
  };
}
