
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

    let selectedEngineTypes = [];
    let selectedEngineTypesNames = []
    document.querySelectorAll('input[name="engine_type"]:checked').forEach((checkbox) => {
        selectedEngineTypes.push(checkbox.value);
        selectedEngineTypesNames.push({"id": checkbox.value,  "name": checkbox.getAttribute('name-attr')});
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

    console.log("selectedEngineTypes:", selectedEngineTypes);


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
        sorting_order: sorting_order,
        engine_type: selectedEngineTypes,

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
        "engine_type": selectedEngineTypesNames,
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
            document.getElementById("table_results_mobile").innerHTML = `<div class="alert alert-danger" role="alert">
            No results found for your search. Please try again with different filters.
            </div>`;
            return;
        }
        update_results(response.data.results, response.data.current_page, response.data.num_pages, response.data.count);
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
    document.getElementById("models_form_mobile").innerHTML = "";

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
            document.getElementById("models_form_mobile").insertAdjacentHTML("beforeend", option);

        });

        update_cars_data();
    })
    .catch(function (error) {
        console.log(error);
    });
    return true;



}

function update_results(data, current_page, total_pages, count) {
    document.getElementById("table_results").innerHTML = "";
    document.getElementById("table_results_mobile").innerHTML = "";
    const windowWidth = window.innerWidth

    let canvas = "";

    data.forEach(element => {
    let display_picture = '';
    if (element.all_media.length > 0 && element.all_media[0].img_url_from_api) { display_picture = element.all_media[0].img_url_from_api;}

        if (windowWidth <= 767){
            canvas += `
    <!--                    For Mobile:-->
                   <div class="d-flex d-md-none flex-column search-result-mobile-wrapper" style="gap:5px;">
                        <div class="d-flex align-items-start" style="gap:10px;">
                                <div class="" style="max-width: 120px;width: 100%;height: 100%;max-height: 98px;min-height: 98px;">
                                        <img 
                                            src="${display_picture}"
                                            class="img-fluid" 
                                            alt="Car 1" 
                                            style="width: 100%;height: inherit;max-height: inherit;object-position: bottom;border-radius: 5px;min-height: inherit;object-fit: cover;"
                                        >
                                </div>
                                <div>
                                    <p class="fs-6 text-start fw-bold m-0 text-primary-color " style="padding-bottom: 6px;">${element.make.name} ${element.model.name} ${element.year}</p>
                                    <div class="d-flex align-items-center " style="gap:2px;">
                                       <p class="text-start text-color m-0" style="width:fit-content;font-size: 12px;">
                                            Price:
                                       </p>
                                        <p class="text-start text-primary-red m-0" style="width:fit-content;font-size: 12px;">
                                            $${(element.price - element.price_discount).toLocaleString()}
                                       </p>
                                    </div>
                                    <div class="d-flex align-items-center " style="gap:2px;">
                                       <p class="text-start text-color m-0" style="width:fit-content;font-size: 12px;">
                                            Engine:
                                       </p>
                                        <p class="text-start text-primary-red m-0" style="width:fit-content;font-size: 12px;">
                                            3.7L
                                       </p>
                                    </div>
                                    <div class="d-flex align-items-center " style="gap:2px;">
                                       <p class="text-start text-color m-0" style="width:fit-content;font-size: 12px;">
                                            Odometer:
                                       </p>
                                        <p class="text-start text-primary-red m-0" style="width:fit-content;font-size: 12px;">
                                          ${element.odometer} mi
                                       </p>
                                    </div>
                                  
                                 
                                </div>
                        </div> 
                    <div class="accordion acc-table" id="carDetailsAccordion_${element.id}">
                                <div class="accordion-item-table">
                                    <h2 class="accordion-header-table" id="heading${element.id}">                                    
                                        <button class="accordion-button-table" onclick="change_accordion_text('accordian_btn_${element.id}')" id="accordian_btn_${element.id}" type="button" data-bs-toggle="collapse" data-bs-target="#collapse${element.id}" aria-expanded="false" aria-controls="collapse${element.id}">
                                            <span class="toggle-text">More Details</span>
                                        </button>
                                    </h2>
                                    <div id="collapse${element.id}" class="accordion-collapse collapse detail-accordion-collapse" aria-labelledby="heading${element.id}" data-bs-parent="#carDetailsAccordion_${element.id}">
                                        <div class="accordion-body-table">
                                            <div class="text-center d-flex flex-wrap" style="gap:12px;">
                                                <div class="d-flex flex-column gap-0.5 text-left">
                                                    <span class="text-color text-sm">
                                                        Body Style:
                                                    </span> 
                                                    <span class="detail-item text-primary-color">
                                                        ${element.body_style.name_en}
                                                    </span>
                                                </div>
                                                <div class="d-flex flex-column gap-0.5 text-left"><span class="text-color text-sm">Fuel Type:</span> <span class="detail-item text-primary-color">${element.fuel.name_en} </span></div>
                                                <div class="d-flex flex-column gap-0.5 text-left"><span class="text-color text-sm">Transmission:</span> <span class="detail-item text-primary-color"> ${element.transmission.name_en} </span></div>
                                                <div class="d-flex flex-column gap-0.5 text-left"><span class="text-color text-sm">Drive:</span> <span class="detail-item text-primary-color">${element.drive.name_en}</span></div>
                                                <div class="d-flex flex-column gap-0.5 text-left"><span class="text-color text-sm">Color:</span> <span class="detail-item text-primary-color"> ${element.color.name_en} </span></div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>                                  
                  </div>           
                        `
        }else{
            canvas += `
    <!--                    For Desktop-->
                   <div class="row g-4 d-none d-md-block">
                               <div class="row g-4">
                                <div class="col-12 col-md-2 " style="margin-top: 20px !important;">
                                    <div class="" style="max-width: 100%;width: 100%;height: 100%;max-height: 110px;">
                                        <img src="${display_picture}"
                                        class="img-fluid" alt="Car 1" style="width: 100%;height: inherit;object-fit: cover;object-position: bottom;">
                                    </div>
                                </div>
                                <div class="col-12 col-md-3 text-left" style="margin-top: 20px !important;">
                                    <p class="fs-6 text-start fw-bold m-0 text-primary-color ">
                                        ${element.make.name} ${element.model.name} ${element.year}
                                    </p>
                                </div>
                                <div class="col-12 col-md-2 text-left text-sm d-flex flex-column align-items-start" style="gap:4px;margin-top: 20px !important;">                                
                                  
                                    <div class="d-flex align-items-center"  style="gap:2px;padding-bottom: 5px;">
                                       <span class="fw-bold">Power:</span>  
                                        <span >${element.fuel.id === 3 ?`${element.motor_power} ${element.motor_power_unit || ""}` : `${element.engine_power} ${element.engine_power_unit || ""}`}</span>
                                    </div>
                                    <div class="d-flex align-items-center"  style="gap:2px;">
                                       <span class="fw-bold">${element.fuel.id === 3 ? "Battery:" : "Engine:"}</span>  
                                         <span >${element.fuel.id === 3 ? `${element.battery_range}` : `${element.engine_type}`}</span>
                                    </div>
                                   
                                 </div>
                                <div class="col-12 col-md-2 text-left text-sm" style="margin-top: 20px !important;">      
                                    <span>${element.odometer} mi</span> 
                                </div>
                               
                                <div class="col-12 col-md-3 d-none d-sm-flex flex-column text-left text-sm" style="gap: 4px;margin-top: 20px !important;">
                                    
                                    <div class="d-flex align-items-center" style="gap:2px;padding-bottom: 5px;">
                                        <span class="fw-bold">Price:</span> 
                                        <span>$${(element.price - element.price_discount).toLocaleString()}</span>
                                    </div>
                                    <div class="d-flex align-items-center"  style="gap:2px;">
                                        <span class="fw-bold">Location:</span>
                                        <span>${element.country.name}</span>
                                     </div>
                                    <a href="/normal-car-details/${element.id}" style="text-decoration: none;">
                                        <button class="btn btn-danger details-button font-medium text-sm d-flex align-items-center justify-content-center" style="width: 100%;max-width:95px;max-height: 28px;margin-top: 20px;margin-left: auto;">
                                            Details
                                        </button>
                                    </a>
                                </div>
                            </div>
                            
                            <div class="accordion acc-table" id="carDetailsAccordion_${element.id}">
                                <div class="accordion-item-table">
                                    <h2 class="accordion-header-table" id="heading${element.id}">                                    
                                        <button class="accordion-button-table" onclick="change_accordion_text('accordian_btn_${element.id}')" id="accordian_btn_${element.id}" type="button" data-bs-toggle="collapse" data-bs-target="#collapse${element.id}" aria-expanded="false" aria-controls="collapse${element.id}">
                                            <span class="toggle-text">More Details</span>
                                        </button>
                                    </h2>
                                    <div id="collapse${element.id}" class="accordion-collapse collapse detail-accordion-collapse" aria-labelledby="heading${element.id}" data-bs-parent="#carDetailsAccordion_${element.id}">
                                        <div class="accordion-body-table">
                                            <div class="row text-center justify-content-between">
                                                <div class="col-md-2 d-flex flex-column gap-0.5 text-left">
                                                    <span class="text-color text-sm">
                                                        Body Style:
                                                    </span> 
                                                    <span class="detail-item text-primary-color">
                                                        ${element.body_style.name_en}
                                                    </span>
                                                </div>
                                                <div class="col-md-2 d-flex flex-column gap-0.5 text-left"><span class="text-color text-sm">Fuel Type:</span> <span class="detail-item text-primary-color">${element.fuel.name_en} </span></div>
                                                <div class="col-md-2 d-flex flex-column gap-0.5 text-left"><span class="text-color text-sm">Transmission:</span> <span class="detail-item text-primary-color"> ${element.transmission.name_en} </span></div>
                                                <div class="col-md-2 d-flex flex-column gap-0.5 text-left"><span class="text-color text-sm">Drive:</span> <span class="detail-item text-primary-color">${element.drive.name_en}</span></div>
                                                <div class="col-md-2 d-flex flex-column gap-0.5 text-left"><span class="text-color text-sm">Color:</span> <span class="detail-item text-primary-color"> ${element.color.name_en} </span></div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>                                  
                        </div>
                        `
        }
    });
    document.getElementById("table_results").innerHTML = canvas;
    document.getElementById("table_results_mobile").innerHTML = canvas;


    if (windowWidth <= 767){
        document.getElementById("total-page-view").innerHTML = `${count} Listings`;
    }else{
        document.getElementById("total-page-view").innerHTML = `Showing page ${current_page} out of ${total_pages} total pages`;
    }

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
