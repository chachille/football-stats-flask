// static/js/main.js

document.addEventListener("DOMContentLoaded", () => {
  const contentPane = document.getElementById("main-content-pane");
  const menuLinks = document.querySelectorAll(".menu-link");
  const tournamentSelect = document.getElementById("tournament-select");
  const teamSelect = document.getElementById("team-select");

  // Function to get the active page and selected tournament
  function getCurrentState() {
    const activeLink = document.querySelector(".menu-link.active");
    const page = activeLink ? activeLink.dataset.page : "overview";
    const tournamentId = tournamentSelect.value;
    const teamId = teamSelect.value;
    console.debug(activeLink);
    if (activeLink.dataset.page == "overview") {
      teamSelect.hidden = true;
      teamSelect.value = "all";
    } else {
      teamSelect.hidden = false;
    }

    return { page, tournamentId, teamId };
  }

  // Function to load content based on current state
  async function loadContent() {
    const { page, tournamentId, teamId } = getCurrentState();
    try {
      const url = `/content/${page}?tournament_id=${tournamentId}&team_id=${teamId}`;
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      const html = await response.text();
      contentPane.innerHTML = html;
    } catch (error) {
      console.error("Error loading page:", error);
      contentPane.innerHTML = "<p>Error loading content. Please try again.</p>";
    }
  }

  // Event listeners
  menuLinks.forEach((link) => {
    link.addEventListener("click", (event) => {
      event.preventDefault();
      menuLinks.forEach((item) => item.classList.remove("active"));
      link.classList.add("active");
      loadContent(); // Load content on menu link click
    });
  });

  tournamentSelect.addEventListener("change", loadContent); // Load content on Tournaments dropdown change
  teamSelect.addEventListener("change", loadContent); // Load content on Teams dropdown change

  // Initial page load
  loadContent();
});

// document.addEventListener("DOMContentLoaded", () => {
//   const contentPane = document.getElementById("main-content-pane");
//   const menuLinks = document.querySelectorAll(".menu-link");

//   // Function to load content into the pane
//   async function loadContent(page) {
//     try {
//       const response = await fetch(`/content/${page}`);
//       if (!response.ok) {
//         throw new Error("Network response was not ok");
//       }
//       const html = await response.text();
//       contentPane.innerHTML = html;
//     } catch (error) {
//       console.error("There was a problem loading the page:", error);
//       contentPane.innerHTML = "<p>Error loading content. Please try again.</p>";
//     }
//   }

//   // Add event listener to each menu link
//   menuLinks.forEach((link) => {
//     link.addEventListener("click", (event) => {
//       event.preventDefault(); // Stop the link from a full refresh

//       // Get the page name from the data attribute
//       const pageName = link.dataset.page;

//       // Update the active class for styling
//       menuLinks.forEach((item) => item.classList.remove("active"));
//       link.classList.add("active");

//       // Load the new content
//       loadContent(pageName);
//     });
//   });

//   // Load the initial content when the page first loads (e.g., the overview page)
//   const initialPage = document.querySelector(".menu-link.active").dataset.page;
//   if (initialPage) {
//     loadContent(initialPage);
//   }
// });
