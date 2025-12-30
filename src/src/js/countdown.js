export function countdown(targetDate) {
  return {
    days: 0,
    hours: 0,
    minutes: 0,
    seconds: 0,
    timer: null,
    update() {
      const now = new Date();
      const diff = targetDate - now;

      if (diff <= 0) {
        this.days = this.hours = this.minutes = this.seconds = 0;
        clearInterval(this.timer);
        return;
      }

      this.days = Math.floor(diff / (1000 * 60 * 60 * 24));
      this.hours = Math.floor((diff / (1000 * 60 * 60)) % 24);
      this.minutes = Math.floor((diff / (1000 * 60)) % 60);
      this.seconds = Math.floor((diff / 1000) % 60);
    },
    start() {
      this.update();
      this.timer = setInterval(() => this.update(), 1000);
    },
  };
}
