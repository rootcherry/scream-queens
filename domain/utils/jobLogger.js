// Simple job logger helper

function logJob({ job_id, queen_id, job_type, status, duration_sec }) {
  let msg = `[JOB ${job_id}] Queen ${queen_id} | Type: ${job_type} | Status: ${status}`;
  if (duration_sec !== undefined) {
    msg += ` | Duration: ${Math.round(duration_sec)}s`;
  }
  console.log(msg);
}

module.exports = logJob;
