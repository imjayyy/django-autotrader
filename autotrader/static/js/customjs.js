var owl = $('.owl-carousel').owlCarousel({
    loop:true,
    margin:10,
    // nav:true,
    responsive:{
        0:{
            items:2
        },
        600:{
            items:3
        },
        1000:{
            items:6
        }
    }
    
})
      // Custom Navigation
      $(".custom-prev").click(function () {
        owl.trigger("prev.owl.carousel");
      });

      $(".custom-next").click(function () {
        owl.trigger("next.owl.carousel");
      });

var swiper_card = new Swiper('.swiper', {
  // Optional parameters
  direction: 'horizontal',
  loop: true,

  // If we need pagination
  pagination: {
    el: '.swiper-pagination',
  },

  // Navigation arrows
  navigation: {
    nextEl: '.swiper-button-next',
    prevEl: '.swiper-button-prev',
  },

  // And if we need scrollbar
  scrollbar: {
    el: '.swiper-scrollbar',
  },
});


  function submit_callback() {
    const name = document.getElementById("name").value.trim();
    const countryCode = document.getElementById("country_code").value;
    const phone = document.getElementById("phone").value.trim();
    const captcha = document.getElementById("captcha").checked;
    const btn = document.getElementById("Callback");

    const phonePattern = /^[\d\s\-\/]+$/;


    if (!name || !countryCode || !phone) {
      alert("Please fill in all fields.");
      return;
    }

    if (!phonePattern.test(phone)) {
      alert("Phone number can only contain digits, spaces, dashes (-), or slashes (/).");
      return;
    }

    if (!captcha) {
      alert("Please verify the captcha before submitting.");
      return;
    }

    btn.disabled = true;
    btn.innerText = "Submitting...";
    
    const formData = new FormData();
    formData.append("name", name);
    formData.append("country_code", countryCode);
    formData.append("phone", phone);

    fetch("/form-submission/", {
      method: "POST",
      body: formData,
      headers: {
        "X-CSRFToken": document.querySelector('meta[name="csrf-token"]').getAttribute('content'),
        "X-Requested-With": "XMLHttpRequest"
      },
    })
    .then(response => response.json())
    .then(data => {
      if (data.status === "success") {
        alert(data.message);
        document.querySelector("form").reset(); // Clear form
      } else {
        alert(data.message);
      }
    })
    .catch(error => {
      alert("Something went wrong. Please try again.");
      console.error(error);
    }).finally(() => {
      // Re-enable button after response
      btn.disabled = false;
      btn.innerText = "Request Callback";
    });
  }
