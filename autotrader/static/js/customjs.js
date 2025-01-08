var owl = $('.owl-carousel').owlCarousel({
    loop:true,
    margin:10,
    // nav:true,
    responsive:{
        0:{
            items:3
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

