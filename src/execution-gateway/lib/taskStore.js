class TaskStore {
  constructor() {
    this.tasks = new Map();
  }

  create(task) {
    this.tasks.set(task.id, task);
    return task;
  }

  get(id) {
    return this.tasks.get(id);
  }

  update(id, patch) {
    const existing = this.tasks.get(id);
    if (!existing) return null;
    const updated = { ...existing, ...patch, updated_at: new Date().toISOString() };
    this.tasks.set(id, updated);
    return updated;
  }
}

module.exports = { TaskStore };
