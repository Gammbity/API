document.addEventListener("DOMContentLoaded", () => {
    const modal = document.getElementById('modal');
    
    // localStorage'da token bor-yo'qligini tekshirish
    const token = localStorage.getItem('token');

    if (!token) {
        modal.classList.add('show');
    }

    const form = document.querySelector(".form");

    form.addEventListener("submit", (e) => {
        e.preventDefault();

        const name = e.target.name.value;
        const username = e.target.username.value;
        const password = e.target.password.value;

        const data = { name, username, password };

        fetch("http://127.0.0.1:5000/submit", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(data),
        })
        .then((response) => response.json())
        .then((result) => {
            console.log(result.token);
            if (result.token){
                localStorage.setItem("token", result.token);
                localStorage.setItem("with_token", false);
                modal.classList.remove('show');
            }
        })
        .catch((error) => {
            console.error("Xatolik yuz berdi:", error);
        });
    });
});

function closeModal() {
    const modal = document.getElementById('modal');
    modal.classList.remove('show'); // Modalni yopish
}
