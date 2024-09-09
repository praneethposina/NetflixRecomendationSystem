document.addEventListener("DOMContentLoaded", function () {
  const input = document.getElementById("movie");
  const suggestions = document.getElementById("suggestions");

  input.addEventListener("input", function () {
    const inputValue = input.value.trim().toLowerCase();
    suggestions.innerHTML = "";

    if (inputValue.length < 3) return;

    fetch("../movies.csv")
      .then((response) => response.text())
      .then((csvData) => {
        const titlesAndYears = parseCSV(csvData);
        const filteredTitles = titlesAndYears.filter((item) =>
          item.title.toLowerCase().includes(inputValue)
        );

        filteredTitles.forEach((item) => {
          const li = document.createElement("li");
          li.textContent = `${item.title} (${item.year})`;
          suggestions.appendChild(li);
        });
      })
      .catch((error) => {
        console.error("Error fetching Netflix titles:", error);
      });
  });

  suggestions.addEventListener("click", function (event) {
    if (event.target.tagName === "LI") {
      const selectedTitle = event.target.textContent.split(" (")[0];
      input.value = selectedTitle;
      suggestions.innerHTML = "";
    }
  });

  input.addEventListener("input", function () {
    input.classList.remove("selected");
  });

  function parseCSV(csvData) {
    const lines = csvData.split("\n");
    const titlesAndYears = [];
    for (let i = 1; i < lines.length; i++) {
      const line = lines[i].trim();
      if (line) {
        const columns = line.split(",");
        const title = columns[1];
        const year = columns[3];
        titlesAndYears.push({ title, year });
      }
    }
    return titlesAndYears;
  }
});

