// Get all FAQ items
const faqItems = document.querySelectorAll('.faq-item');

// Function to toggle the answer visibility
function toggleAnswer() {
  this.classList.toggle('active');
  const answer = this.querySelector('.faq-answer');
  if (this.classList.contains('active')) {
    answer.style.display = 'block';
  } else {
    answer.style.display = 'none';
  }
}

// Attach click event listener to each FAQ item
faqItems.forEach(item => {
  item.addEventListener('click', toggleAnswer);
});
