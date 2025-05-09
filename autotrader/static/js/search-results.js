
document.addEventListener("DOMContentLoaded", function() {
    let params = getQueryParams();
    console.log(params);    
    if ("searchByText" in params) {
        console.log("Search value:", params.searchByText);
        return
    }

    let selectMake = document.querySelectorAll(`input[name="make"]`);
    selectMake.forEach((element) => {
        if (element.value === params.make) {
            element.checked = true;
        }
    });

    Object.entries(params).forEach(([key, value]) => {
        let input_form_elements = document.querySelectorAll(`input[name="${key}"]`);
        input_form_elements.forEach((input_form_element) => {
            if (input_form_element) {
            if (input_form_element.type === "checkbox") {
                if(input_form_element.value === value){
                input_form_element.checked = true;}
            }
            else {
                input_form_element.value = value;}
            
        }});    
    });
        
    

    Promise.resolve(update_models()).then(() => {
        setTimeout(() => {
            let selectModel = document.querySelectorAll(`input[name="model"]`);
            selectModel.forEach((element) => {
                if (params.model && element.value === params.model) {
                    element.checked = true;
                }
            });
            update_cars_data();

        }, 500); // Delay for 500ms to ensure models are loaded
    });


});



function change_accordion_text(accordion_id) {
    const button = document.getElementById(accordion_id);
    const toggleText = button.querySelector(".toggle-text");    
    if (toggleText.textContent === "More Details") {
        toggleText.textContent = "Less Details";
    } 
    else {
        toggleText.textContent = "More Details"
    }
}



function getQueryParams() {
    const params = new URLSearchParams(window.location.search);
    let queryObject = {};
    
    params.forEach((value, key) => {
        if (queryObject[key]) {
            // Convert to array if multiple values exist for the same key
            queryObject[key] = [].concat(queryObject[key], value);
        } else {
            queryObject[key] = value;
        }
    });

    return queryObject;
}


function update_cars_data(page=1){


    let selectedMakes = [];
    let selectedMakesNames = [] 
    document.querySelectorAll('input[name="make"]:checked').forEach((checkbox) => {
        selectedMakes.push(checkbox.value);
        selectedMakesNames.push( {"id": checkbox.value,  "name": checkbox.getAttribute('name-attr')} ); 
    });


    let selectedModels = [];
    let selectedModelsNames = []
    document.querySelectorAll('input[name="model"]:checked').forEach((checkbox) => {
        selectedModels.push(checkbox.value);
        selectedModelsNames.push({"id": checkbox.value,  "name": checkbox.getAttribute('name-attr')});
    });

    let selectedTransmissions = [];
    let selectedTransmissionsNames = []
    document.querySelectorAll('input[name="Transmission"]:checked').forEach((checkbox) => {
        selectedTransmissions.push(checkbox.value);
        selectedTransmissionsNames.push({"id": checkbox.value,  "name": checkbox.getAttribute('name-attr')});
    });

    let selectedDrives = [];
    let selectedDrivesNames = []
    document.querySelectorAll('input[name="Drive"]:checked').forEach((checkbox) => {
        selectedDrives.push(checkbox.value);
        selectedDrivesNames.push({"id": checkbox.value,  "name": checkbox.getAttribute('name-attr')});
    });

    let selectedFuels = [];
    let selectedFuelsNames = []
    document.querySelectorAll('input[name="fuel"]:checked').forEach((checkbox) => {
        selectedFuels.push(checkbox.value);
        selectedFuelsNames.push({"id": checkbox.value,  "name": checkbox.getAttribute('name-attr')});
    });

    let selectedBodyStyles = [];
    let selectedBodyStylesNames = []
    document.querySelectorAll('input[name="BodyStyle"]:checked').forEach((checkbox) => {
        selectedBodyStyles.push(checkbox.value);
        selectedBodyStylesNames.push({"id": checkbox.value,  "name": checkbox.getAttribute('name-attr')});
    });

    let selectedCountries = [];
    let selectedCountriesNames = []
    document.querySelectorAll('input[name="country"]:checked').forEach((checkbox) => {
        selectedCountries.push(checkbox.value);
        selectedCountriesNames.push({"id": checkbox.value,  "name": checkbox.getAttribute('name-attr')});
    });
    let selectedColors = [];
    let selectedColorsNames = []
    document.querySelectorAll('input[name="color"]:checked').forEach((checkbox) => {
        selectedColors.push(checkbox.value);
        selectedColorsNames.push({"id": checkbox.value,  "name": checkbox.getAttribute('name-attr')});
    }
    );

    let odometerMin = document.querySelector('input[name="odometer_min"]').value;
    let odometerMax = document.querySelector('input[name="odometer_max"]').value;

    let priceMin = document.querySelector('input[name="price_min"]').value;
    let priceMax = document.querySelector('input[name="price_max"]').value;


    let year_min = document.querySelector('input[name="year_min"]').value;
    let year_max = document.querySelector('input[name="year_max"]').value;

    let sorting_by = document.getElementById('sortBy').value;
    let sorting_order = document.getElementById('sortBtn').getAttribute('data-order');

    let filterParams = {
        page: page,
        make: selectedMakes,
        model: selectedModels,
        transmission: selectedTransmissions,
        drives: selectedDrives,
        fuels: selectedFuels,
        body_style: selectedBodyStyles,
        odometerMin: odometerMin,
        odometerMax: odometerMax,
        priceMin: priceMin,
        priceMax: priceMax,
        country: selectedCountries,
        color: selectedColors,
        year_min: year_min,
        year_max: year_max, 

        sorting_by: sorting_by,
        sorting_order: sorting_order
    };

    let filterTags = {
        "make": selectedMakesNames,
        "model": selectedModelsNames,
        "Transmission": selectedTransmissionsNames,
        "Drive": selectedDrivesNames,
        "fuel": selectedFuelsNames,
        "BodyStyle": selectedBodyStylesNames,
        "country": selectedCountriesNames,
        "color": selectedColors,
        "odometer_min": odometerMin,
        "odometer_max": odometerMax,
        "price_min": priceMin,
        "price_max": priceMax,
        "year_min": year_min,
        "year_max": year_max,
    }

    console.log("filterTags:", filterTags);

    axios.get('/api/search-api/', {
        params: filterParams
    })
    .then(function (response) {
        console.log("resp:", response.data);
        if (response.data.count === 0 ){
            document.getElementById("table_results").innerHTML = `<div class="alert alert-danger" role="alert">
            No results found for your search. Please try again with different filters.
            </div>`;
            return;
        }
        update_results(response.data.results, response.data.current_page, response.data.num_pages);
        show_filters(filterTags);
    }).catch(function (error) {
        console.log(error);})

            
        
}


function clear_tag(key, value) {
    // let tag = document.querySelector(`.filter-tag:contains('${key} : ${value}')`);
    const url = new URL(window.location.href); // Get the current URL
    url.search = ''; // Remove the search (query parameters)
    window.history.replaceState({}, document.title, url.toString()); 

    console.log(key, value);


    let tag = document.querySelector(`.filter-tag[key="${key}"][value="${value}"]`);
    if (tag) {
        tag.remove();
    }
    let checkbox = document.querySelector(`input[name="${key}"][value="${value}"]`);
    if (checkbox) {
        checkbox.checked = false;
    }
    else{
        let text_element = document.querySelector(`input[name="${key}"]`);
        if (text_element) {
            text_element.value = "";
        }
    }

    update_cars_data();
}


function show_filters(filter_tags) {
    document.getElementById("filter-tags").innerHTML = "";

    
    Object.entries(filter_tags).forEach(([key, value]) => {
        if (Array.isArray(value) && value.length > 0) {
            value.forEach(item => {
                if (item.name) {
                    let tag = create_tag(key, item.id, item.name);
                    document.getElementById("filter-tags").insertAdjacentHTML("beforeend", tag);
                }
            });
        } else if (typeof value === "string" && value.trim() !== "") {
            let tag = create_tag(key, value, value);
            document.getElementById("filter-tags").insertAdjacentHTML("beforeend", tag);
        }
    });
}

function create_tag(key, value, name) {
    return `<span class="badge bg-dark filter-tag" key="${key}" value="${value}" >${key} : ${name} 
                <button class="btn-close btn-close-white btn-sm ms-2" onclick="clear_tag('${key}', '${value}')"></button>
            </span>`;
}

function update_models() {
    // Clear the existing models
    document.getElementById("models_form").innerHTML = "";

    let selectedMakes = [];
    document.querySelectorAll('input[name="make"]:checked').forEach((checkbox) => {
        selectedMakes.push(checkbox.value);
    });

    // Send request to get models
    axios.get('/api/models-from-id/', {
        params: { makes: selectedMakes }
    })
    .then(function (response) {

        response.data.forEach(element => {
            var option = `
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" id="model_${element.id}" name-attr=${element.name} name="model" value="${element.id}" onclick="update_cars_data()">
                    <label class="form-check-label text-start"  style="display: block;" name-attr=${element.name} for="model_${element.id}">
                        ${element.name}
                    </label>
                </div>
            `;

            document.getElementById("models_form").insertAdjacentHTML("beforeend", option);
        });

        update_cars_data();
    })
    .catch(function (error) {
        console.log(error);
    });
    return true;



}

function update_results(data, current_page, total_pages) {
    document.getElementById("table_results").innerHTML = "";
    let canvas = "";

    data.forEach(element => {
    let display_picture = '';
    if (element.all_media.length > 0 && element.all_media[0].img_url_from_api) { display_picture = element.all_media[0].img_url_from_api;}

    canvas += `<div class="row g-4">
                            <div class="col-12 col-md-2">
                                <img src="${display_picture}"
                                    class="img-fluid" alt="Car 1" style="width: 100px;">
                            </div>
                            <div class="col-12 col-md-2">
                                <strong class="fs-6 text-start">${element.make.name} ${element.model.name} ${element.year}</strong><br>
                                <small class=" text-start">Lot #69400444</small>
                            </div>
                            <div class="col-12 col-md-2">                                
                                Fuel Type: ${element.fuel.name_en} <br>
                                ${element.transmission.name_en} ${element.drive.name_en}
                            </div>
                            <div class="col-12 col-md-2">
                                
                                Odometer: ${element.odometer} mi
                            </div>
                            <div class="col-12 col-md-2 d-none d-sm-block">
                               ${element.country.name}<br>
                                
                            </div>
                            <div class="col-12 col-md-2 d-none d-sm-block">
                                Buy now: $${element.price}<br>
                                <a href="/normal-car-details/${element.id}">
                                <button class="btn btn-danger details-button mt-2">Details</button>
                                </a>
                            </div>
                        
                        <div class="accordion acc-table my-2" id="carDetailsAccordion_${element.id}">
                            <div class="accordion-item-table">
                                <h2 class="accordion-header-table" id="heading${element.id}">                                    
                                    <button class="accordion-button-table" onclick="change_accordion_text('accordian_btn_${element.id}')" id="accordian_btn_${element.id}" type="button" data-bs-toggle="collapse" data-bs-target="#collapse${element.id}" aria-expanded="false" aria-controls="collapse${element.id}">
                                        <span class="toggle-text">More Details</span>
                                    </button>
                                </h2>
                                <div id="collapse${element.id}" class="accordion-collapse collapse" aria-labelledby="heading${element.id}" data-bs-parent="#carDetailsAccordion_${element.id}">
                                    <div class="accordion-body-table">
                                        <div class="row text-center">
                                            <div class="col-md-2"><span class="text-muted">Body Style:</span> <span class="detail-item">${element.body_style.name_en}</span></div>
                                            <div class="col-md-2"><span class="text-muted">Fuel Type:</span> <span class="detail-item">${element.fuel.name_en} </span></div>
                                            <div class="col-md-2"><span class="text-muted">Transmission:</span> <span class="detail-item"> ${element.transmission.name_en} </span></div>
                                            <div class="col-md-2"><span class="text-muted">Drive:</span> <span class="detail-item">${element.drive.name_en}</span></div>
                                            <div class="col-md-2"><span class="text-muted">Color:</span> <span class="detail-item"> ${element.color.name_en} </span></div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>                                  
                    </div>
                        
                        
                        `});
    document.getElementById("table_results").innerHTML = canvas;
    
    document.getElementById("total-page-view").innerHTML = `Showing page ${current_page} out of ${total_pages} total pages`;

    let pagination_buttons = "";
    document.getElementById("search-pagination").innerHTML = pagination_buttons;

    for (let i = 1; i <= total_pages; i++) {
        if (i === current_page) {
            pagination_buttons += `<a class="page-link text-white rounded" style="background: red"><li class="page-item ">${i}</li></a>`;
        } else {
            pagination_buttons += `<a class="page-link text-danger rounded" onclick="update_cars_data( ${i} )"><li class="page-item">${i}</li></a>`;
        }        
    }

    document.getElementById("search-pagination").innerHTML = pagination_buttons;

}
