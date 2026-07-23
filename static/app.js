document.querySelector('form').addEventListener('submit', function(event) {
    
    event.preventDefault(); 

   
    const itemName = document.getElementById('item').value;
    const itemAmount = document.getElementById('amount').value;

    console.log("Expense added via Frontend:");
    console.log("Item:", itemName);
    console.log("Amount: $", itemAmount);

    alert(`Captured: ${itemName} for $${itemAmount}`);
});